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
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base as base_views

from horizon import exceptions
import horizon.forms
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs
from horizon.utils import memoized
import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import forms
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui.infrastructure.overcloud import tabs
from tuskar_ui.infrastructure.overcloud.workflows import undeployed


class OvercloudMixin(object):
    @memoized.memoized
    def get_overcloud(self):
        overcloud_id = self.kwargs['overcloud_id']

        try:
            overcloud = api.Overcloud.get(self.request, overcloud_id)
        except Exception:
            msg = _("Unable to retrieve deployment.")
            redirect = reverse('horizon:infrastructure:overcloud:index')
            exceptions.handle(self.request, msg, redirect=redirect)

        return overcloud


class OvercloudRoleMixin(object):
    @memoized.memoized
    def get_role(self, overcloud):
        role_id = self.kwargs['role_id']

        try:
            role = api.OvercloudRole.get(self.request, role_id)
        except Exception:
            msg = _("Unable to retrieve overcloud role.")
            redirect = reverse('horizon:infrastructure:overcloud:detail',
                               args=(overcloud.id,))
            exceptions.handle(self.request, msg, redirect=redirect)

        return role


class IndexView(base_views.RedirectView):
    permanent = False

    def get_redirect_url(self):
        overcloud = api.Overcloud.get(self.request, 1)
        if overcloud is not None and overcloud.stack is not None and any([
            overcloud.is_deployed,
            overcloud.is_deploying,
            overcloud.is_failed,
        ]):
            redirect = reverse('horizon:infrastructure:overcloud:detail',
                               args=(overcloud.id,))
        else:
            redirect = reverse('horizon:infrastructure:overcloud:create')
        return redirect


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = undeployed.Workflow
    template_name = 'infrastructure/_fullscreen_workflow_base.html'


class DetailView(horizon_tabs.TabView, OvercloudMixin):
    tab_group_class = tabs.DetailTabs
    template_name = 'infrastructure/overcloud/detail.html'

    def get_tabs(self, request, **kwargs):
        overcloud = self.get_overcloud()
        return self.tab_group_class(request, overcloud=overcloud, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['overcloud'] = self.get_overcloud()
        return context


class OvercloudRoleView(horizon_tables.DataTableView,
                        OvercloudRoleMixin, OvercloudMixin):
    table_class = tables.OvercloudRoleNodeTable
    template_name = 'infrastructure/overcloud/overcloud_role.html'

    @memoized.memoized
    def _get_nodes(self, overcloud, role):
        resources = overcloud.resources(role, with_joins=True)
        return [r.node for r in resources]

    def get_data(self):
        overcloud = self.get_overcloud()
        role = self.get_role(overcloud)

        return self._get_nodes(overcloud, role)

    def get_context_data(self, **kwargs):
        context = super(OvercloudRoleView, self).get_context_data(**kwargs)

        overcloud = self.get_overcloud()
        role = self.get_role(overcloud)

        context['role'] = role
        context['image_name'] = role.image_name
        context['nodes'] = self._get_nodes(overcloud, role)

        return context


class OvercloudRoleEdit(horizon.forms.ModalFormView, OvercloudRoleMixin):
    form_class = forms.OvercloudRoleForm
    success_url = 'horizon:infrastructure:overcloud:create'
    template_name = 'infrastructure/overcloud/role_edit.html'

    def get_form_kwargs(self):
        role = self.get_role(1)
        return {
            'initial': {
                'id': role.id,
            }
        }
