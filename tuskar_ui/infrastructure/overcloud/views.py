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
import novaclient

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base as base_views

import heatclient
from horizon import exceptions as horizon_exceptions
import horizon.forms
from horizon import messages
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs
from horizon.utils import memoized
import horizon.workflows
from openstack_dashboard.api import nova

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import forms
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui.infrastructure.overcloud import tabs
from tuskar_ui.infrastructure.overcloud.workflows import scale
from tuskar_ui.infrastructure.overcloud.workflows import undeployed


INDEX_URL = 'horizon:infrastructure:overcloud:index'
DETAIL_URL = 'horizon:infrastructure:overcloud:detail'
CREATE_URL = 'horizon:infrastructure:overcloud:create'
UNDEPLOY_IN_PROGRESS_URL = (
    'horizon:infrastructure:overcloud:undeploy_in_progress')


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


class IndexView(base_views.RedirectView):
    permanent = False

    def get_redirect_url(self):
        try:
            # TODO(lsmola) implement this properly when supported by API
            plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        except heatclient.exc.HTTPNotFound:
            plan = None

        redirect = None
        if plan is None:
            redirect = reverse(CREATE_URL)
        elif plan.stack.is_deleting or plan.stack.is_delete_failed:
            redirect = reverse(UNDEPLOY_IN_PROGRESS_URL,
                               args=(plan.id,))
        else:
            redirect = reverse(DETAIL_URL,
                               args=(plan.id,))

        return redirect


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = undeployed.Workflow
    template_name = 'infrastructure/_fullscreen_workflow_base.html'


class DetailView(horizon_tabs.TabView, OvercloudPlanMixin):
    tab_group_class = tabs.DetailTabs
    template_name = 'infrastructure/overcloud/detail.html'

    def get_tabs(self, request, **kwargs):
        plan = self.get_plan()
        return self.tab_group_class(request, plan=plan, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['plan'] = self.get_plan()
        context['stack'] = self.get_plan().stack
        return context


class UndeployConfirmationView(horizon.forms.ModalFormView):
    form_class = forms.UndeployOvercloud
    template_name = 'infrastructure/overcloud/undeploy_confirmation.html'

    def get_success_url(self):
        return reverse(INDEX_URL)

    def get_context_data(self, **kwargs):
        context = super(UndeployConfirmationView,
                        self).get_context_data(**kwargs)
        context['plan_id'] = self.kwargs['plan_id']
        return context

    def get_initial(self, **kwargs):
        initial = super(UndeployConfirmationView, self).get_initial(**kwargs)
        initial['plan_id'] = self.kwargs['plan_id']
        return initial


class UndeployInProgressView(horizon_tabs.TabView, OvercloudPlanMixin, ):
    tab_group_class = tabs.UndeployInProgressTabs
    template_name = 'infrastructure/overcloud/detail.html'

    def get_overcloud_plan_or_redirect(self):
        try:
            # TODO(lsmola) implement this properly when supported by API
            plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        except heatclient.exc.HTTPNotFound:
            plan = None

        if plan is None:
            redirect = reverse(CREATE_URL)
            messages.success(self.request,
                             _("Undeploying of the Overcloud has finished."))
            raise horizon_exceptions.Http302(redirect)
        elif plan.stack.is_deleting or plan.stack.is_delete_failed:
            return plan
        else:
            messages.error(self.request,
                           _("Overcloud is not being undeployed."))
            redirect = reverse(DETAIL_URL,
                               args=(plan.id,))
            raise horizon_exceptions.Http302(redirect)

    def get_tabs(self, request, **kwargs):
        plan = self.get_overcloud_plan_or_redirect()
        return self.tab_group_class(request, plan=plan, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UndeployInProgressView,
                        self).get_context_data(**kwargs)
        context['plan'] = self.get_overcloud_plan_or_redirect()
        return context


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


class OvercloudRoleView(horizon_tables.DataTableView,
                        OvercloudRoleMixin, OvercloudPlanMixin):
    table_class = tables.OvercloudRoleNodeTable
    template_name = 'infrastructure/overcloud/overcloud_role.html'

    @memoized.memoized
    def _get_nodes(self, plan, role):
        resources = plan.stack.resources_by_role(role, with_joins=True)
        return [r.node for r in resources]

    def get_data(self):
        plan = self.get_plan()
        redirect = reverse(DETAIL_URL,
                           args=(plan.id,))
        role = self.get_role(redirect)
        return self._get_nodes(plan, role)

    def get_context_data(self, **kwargs):
        context = super(OvercloudRoleView, self).get_context_data(**kwargs)

        plan = self.get_plan()
        redirect = reverse(DETAIL_URL,
                           args=(plan.id,))
        role = self.get_role(redirect)
        context['role'] = role
        context['image_name'] = role.image_name
        context['nodes'] = self._get_nodes(plan, role)

        try:
            context['flavor'] = nova.flavor_get(self.request, role.flavor_id)
        except novaclient.exceptions.NotFound:
            context['flavor'] = None
        except Exception:
            msg = _('Unable to retrieve flavor.')
            horizon.exceptions.handle(self.request, msg)
        return context


class OvercloudRoleEdit(horizon.forms.ModalFormView, OvercloudRoleMixin):
    form_class = forms.OvercloudRoleForm
    template_name = 'infrastructure/overcloud/role_edit.html'

    def get_success_url(self):
        return reverse(CREATE_URL)

    def get_initial(self):
        role = self.get_role()
        return {
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'image_name': role.image_name,
            'flavor_id': role.flavor_id,
        }
