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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import workflows
from openstack_dashboard.api import glance

from tuskar_ui import api
from tuskar_ui.infrastructure.node_profiles \
    import tables as node_profiles_tables
from tuskar_ui.infrastructure.node_profiles \
    import workflows as node_profiles_workflows


def image_get(request, image_id, error_message):
    # TODO(dtantsur): there should be generic way to handle exceptions
    try:
        return glance.image_get(request, image_id)
    except Exception:
        exceptions.handle(request, error_message)


class IndexView(tables.DataTableView):
    table_class = node_profiles_tables.NodeProfilesTable
    template_name = 'infrastructure/node_profiles/index.html'

    def get_data(self):
        node_profiles = api.NodeProfile.list(self.request)
        node_profiles.sort(key=lambda np: (np.vcpus, np.ram, np.disk))
        return node_profiles


class CreateView(workflows.WorkflowView):
    workflow_class = node_profiles_workflows.CreateNodeProfile
    template_name = 'infrastructure/node_profiles/create.html'


class DetailView(tables.DataTableView):
    table_class = node_profiles_tables.NodeProfileRolesTable
    template_name = 'infrastructure/node_profiles/details.html'
    error_redirect = reverse_lazy('horizon:infrastructure:node_profiles:index')

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['node_profile'] = api.NodeProfile.get(
            self.request,
            kwargs.get('flavor_id'),
            _error_redirect=self.error_redirect
        )
        context['kernel_image'] = image_get(
            self.request,
            context['node_profile'].kernel_image_id,
            error_message=_("Cannot get kernel image details")
        )
        context['ramdisk_image'] = image_get(
            self.request,
            context['node_profile'].ramdisk_image_id,
            error_message=_("Cannot get ramdisk image details")
        )
        return context

    def get_data(self):
        return [role for role in api.OvercloudRole.list(self.request)
                if role.flavor_id == self.kwargs.get('flavor_id')]
