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
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs
from horizon.utils import memoized
import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import forms
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui.infrastructure.overcloud import tabs
from tuskar_ui.infrastructure.overcloud.workflows import undeployed


class IndexView(base_views.RedirectView):
    permanent = False

    def get_redirect_url(self):
        try:
             # TODO(lsmola) implement this properly when supported by API
            overcloud = api.Overcloud.get_the_overcloud(self.request)
        except Exception:
            overcloud = None

        if overcloud is not None:
            # TODO(lsmola) there can be a short period when overcloud
            # is created, but stack not. So we have to make sure we have
            # missing stack under control as a new STATE
            # Also when deleting now, it first deletes Overcloud then Stack
            # because stack takes much longer to delete. But we can probably
            # ignore it for now and fix the worflow on API side.
            redirect = reverse('horizon:infrastructure:overcloud:detail',
                               args=(overcloud.id,))
        else:
            redirect = reverse('horizon:infrastructure:overcloud:create')
        return redirect


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = undeployed.Workflow
    template_name = 'infrastructure/_fullscreen_workflow_base.html'


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.DetailTabs
    template_name = 'infrastructure/overcloud/detail.html'

    @memoized.memoized_method
    def get_data(self):
        overcloud_id = self.kwargs['overcloud_id']
        try:
            return api.Overcloud.get(self.request, overcloud_id)
        except Exception:
            msg = _("Unable to retrieve deployment.")
            redirect = reverse('horizon:infrastructure:overcloud:index')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_tabs(self, request, **kwargs):
        overcloud = self.get_data()
        return self.tab_group_class(request, overcloud=overcloud, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['overcloud'] = self.get_data()
        return context


class UndeployConfirmationView(horizon.forms.ModalFormView):
    form_class = forms.UndeployOvercloud
    template_name = 'infrastructure/overcloud/undeploy_confirmation.html'

    def get_success_url(self):
        return reverse('horizon:infrastructure:overcloud:index')

    def get_context_data(self, **kwargs):
        context = super(UndeployConfirmationView,
                        self).get_context_data(**kwargs)
        context['overcloud_id'] = self.kwargs['overcloud_id']
        return context

    def get_initial(self, **kwargs):
        initial = super(UndeployConfirmationView, self).get_initial(**kwargs)
        initial['overcloud_id'] = self.kwargs['overcloud_id']
        return initial


class OvercloudRoleView(horizon_tables.DataTableView):
    table_class = tables.OvercloudRoleNodeTable
    template_name = 'infrastructure/overcloud/overcloud_role.html'

    def get_data(self):
        overcloud = self._get_overcloud()
        role = self._get_role(overcloud)

        return self._get_nodes(overcloud, role)

    def get_context_data(self, **kwargs):
        context = super(OvercloudRoleView, self).get_context_data(**kwargs)

        overcloud = self._get_overcloud()
        role = self._get_role(overcloud)

        context['role'] = role
        context['image_name'] = role.image_name
        context['nodes'] = self._get_nodes(overcloud, role)

        return context

    @memoized.memoized
    def _get_nodes(self, overcloud, role):
        resources = overcloud.resources(role, with_joins=True)
        return [r.node for r in resources]

    @memoized.memoized
    def _get_overcloud(self):
        overcloud_id = self.kwargs['overcloud_id']

        try:
            overcloud = api.Overcloud.get(self.request, overcloud_id)
        except Exception:
            msg = _("Unable to retrieve deployment.")
            redirect = reverse('horizon:infrastructure:overcloud:index')
            exceptions.handle(self.request, msg, redirect=redirect)

        return overcloud

    @memoized.memoized
    def _get_role(self, overcloud):
        role_id = self.kwargs['role_id']

        try:
            role = api.OvercloudRole.get(self.request, role_id)
        except Exception:
            msg = _("Unable to retrieve overcloud role.")
            redirect = reverse('horizon:infrastructure:overcloud:detail',
                               args=(overcloud.id,))
            exceptions.handle(self.request, msg, redirect=redirect)

        return role
