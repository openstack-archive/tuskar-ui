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
from horizon import views
from horizon import workflows
from openstack_dashboard.api import glance

from tuskar_ui import api
from tuskar_ui.infrastructure.node_profiles \
    import tables as node_profiles_tables
from tuskar_ui.infrastructure.node_profiles \
    import workflows as node_profiles_workflows


def call_and_handle_errors(func, request, *args, **kwargs):
    # TODO(dtantsur): move this to tiskar_ui.api
    _error_message = kwargs.pop('_error_message')
    _error_default = kwargs.pop('_error_default', None)
    _error_redirect = kwargs.pop('_error_redirect', None)
    _error_ignore = kwargs.pop('_error_ignore', False)
    try:
        return func(request, *args, **kwargs)
    except Exception:
        exceptions.handle(request, _error_message,
                          ignore=_error_ignore,
                          redirect=_error_redirect)
        return _error_default


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


class DetailView(views.APIView):
    template_name = 'infrastructure/node_profiles/details.html'
    error_redirect = reverse_lazy('horizon:infrastructure:node_profiles:index')

    def get_data(self, request, context, *args, **kwargs):
        context['node_profile'] = api.NodeProfile.get(
            request,
            kwargs.get('flavor_id'),
            _error_redirect=self.error_redirect
        )
        context['kernel_image'] = call_and_handle_errors(
            glance.image_get,
            request,
            context['node_profile'].kernel_image_id,
            _error_message=_("Cannot get kernel image details")
        )
        context['ramdisk_image'] = call_and_handle_errors(
            glance.image_get,
            request,
            context['node_profile'].ramdisk_image_id,
            _error_message=_("Cannot get ramdisk image details")
        )
        return context
