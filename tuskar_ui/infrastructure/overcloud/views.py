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
from openstack_dashboard.api import nova

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import forms
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui.infrastructure.overcloud import tabs
from tuskar_ui.infrastructure.overcloud.workflows import scale
from tuskar_ui.infrastructure.overcloud.workflows import undeployed


INDEX_URL = 'horizon:infrastructure:overcloud:index'


class OvercloudMixin(object):
    @memoized.memoized
    def get_overcloud(self, redirect=None):
        if redirect is None:
            redirect = reverse(INDEX_URL)
        overcloud_id = self.kwargs['overcloud_id']
        try:
            overcloud = api.Overcloud.get(self.request, overcloud_id)
        except Exception:
            msg = _("Unable to retrieve deployment.")
            exceptions.handle(self.request, msg, redirect=redirect)

        return overcloud


class OvercloudRoleMixin(object):
    @memoized.memoized
    def get_role(self, redirect=None):
        role_id = self.kwargs['role_id']
        try:
            role = api.OvercloudRole.get(self.request, role_id)
        except Exception:
            msg = _("Unable to retrieve overcloud role.")
            exceptions.handle(self.request, msg, redirect=redirect)
        return role


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


class Scale(horizon.workflows.WorkflowView, OvercloudMixin):
    workflow_class = scale.Workflow

    def get_initial(self):
        overcloud = self.get_overcloud()
        role_counts = dict((
            (count['overcloud_role_id'], 'default'),
            count['num_nodes'],
        ) for count in overcloud.counts)
        return {
            'overcloud_id': overcloud.id,
            'role_counts': role_counts,
        }


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
        redirect = reverse('horizon:infrastructure:overcloud:detail',
                           args=(overcloud.id,))
        role = self.get_role(redirect)
        return self._get_nodes(overcloud, role)

    def get_context_data(self, **kwargs):
        context = super(OvercloudRoleView, self).get_context_data(**kwargs)

        overcloud = self.get_overcloud()
        redirect = reverse('horizon:infrastructure:overcloud:detail',
                           args=(overcloud.id,))
        role = self.get_role(redirect)
        context['role'] = role
        context['image_name'] = role.image_name
        context['nodes'] = self._get_nodes(overcloud, role)

        try:
            context['flavor'] = nova.flavor_get(self.request, role.flavor_id)
        except Exception:
            msg = _('Unable to retrieve node profile.')
            horizon.exceptions.handle(self.request, msg)
        return context


class OvercloudRoleEdit(horizon.forms.ModalFormView, OvercloudRoleMixin):
    form_class = forms.OvercloudRoleForm
    template_name = 'infrastructure/overcloud/role_edit.html'

    def get_success_url(self):
        return reverse('horizon:infrastructure:overcloud:create')

    def get_initial(self):
        role = self.get_role()
        return {
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'image_name': role.image_name,
            'flavor_id': role.flavor_id,
        }
