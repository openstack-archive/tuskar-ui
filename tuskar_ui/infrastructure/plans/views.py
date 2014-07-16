# -*- coding: utf8 -*-
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from django.core.urlresolvers import reverse

from horizon.utils import memoized
import horizon.workflows
import horizon.tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.plans import tabs
from tuskar_ui.infrastructure.plans.workflows import create
from tuskar_ui.infrastructure.plans.workflows import scale


INDEX_URL = 'horizon:infrastructure:plans:index'
CREATE_URL = 'horizon:infrastructure:plans:create'
OVERCLOUD_INDEX_URL = 'horizon:infrastructure:overcloud:index'


class OvercloudPlanMixin(object):
    @memoized.memoized
    def get_plan(self, redirect=None):
        if redirect is None:
            redirect = reverse(INDEX_URL)
        plan_id = self.kwargs['plan_id']
        plan = api.tuskar.OvercloudPlan.get(self.request, plan_id,
                                            _error_redirect=redirect)
        return plan


class OvercloudRoleMixin(object):
    @memoized.memoized
    def get_role(self, redirect=None):
        role_id = self.kwargs['role_id']
        role = api.tuskar.OvercloudRole.get(self.request, role_id,
                                            _error_redirect=redirect)
        return role


class IndexView(horizon.tabs.TabView, OvercloudPlanMixin):
    tab_group_class = tabs.PlansTabs
    template_name = 'infrastructure/plans/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = create.Workflow
    template_name = 'infrastructure/_fullscreen_workflow_base.html'


class Scale(horizon.workflows.WorkflowView, OvercloudPlanMixin):
    workflow_class = scale.Workflow

    def get_context_data(self, **kwargs):
        context = super(Scale, self).get_context_data(**kwargs)
        context['plan_id'] = self.kwargs['plan_id']
        return context

    def get_initial(self):
        plan = self.get_plan()
        overcloud_roles = dict((overcloud_role.id, overcloud_role)
                               for overcloud_role in
                               api.tuskar.OvercloudRole.list(self.request))

        role_counts = dict((
            (count['overcloud_role_id'],
             overcloud_roles[count['overcloud_role_id']].flavor_id),
            count['num_nodes'],
        ) for count in plan.counts)
        return {
            'plan_id': plan.id,
            'role_counts': role_counts,
        }
