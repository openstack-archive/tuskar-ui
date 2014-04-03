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

import horizon.exceptions
import horizon.tables
import horizon.tabs
import horizon.workflows

import tuskar_ui.api
from tuskar_ui.infrastructure.flavors import tables
from tuskar_ui.infrastructure.flavors import tabs
from tuskar_ui.infrastructure.flavors import workflows


def image_get(request, image_id, error_message):
    # TODO(dtantsur): there should be generic way to handle exceptions
    try:
        return tuskar_ui.api.image_get(request, image_id)
    except Exception:
        horizon.exceptions.handle(request, error_message)


class IndexView(horizon.tabs.TabbedTableView):
    tab_group_class = tabs.FlavorTabs
    template_name = 'infrastructure/flavors/index.html'


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = workflows.CreateFlavor
    template_name = 'infrastructure/flavors/create.html'

    def get_initial(self):
        suggestion_id = self.kwargs.get('suggestion_id')
        if not suggestion_id:
            return super(CreateView, self).get_initial()
        node = tuskar_ui.api.Node.get(self.request, suggestion_id)
        suggestion = tabs.FlavorSuggestion.from_node(node)
        return {
            'name': suggestion.name,
            'vcpus': suggestion.vcpus,
            'memory_mb': suggestion.ram,
            'disk_gb': suggestion.disk,
            'arch': suggestion.cpu_arch,
        }


class DetailView(horizon.tables.DataTableView):
    table_class = tables.FlavorRolesTable
    template_name = 'infrastructure/flavors/details.html'
    error_redirect = reverse_lazy('horizon:infrastructure:flavors:index')

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['flavor'] = tuskar_ui.api.Flavor.get(
            self.request,
            kwargs.get('flavor_id'),
            _error_redirect=self.error_redirect
        )
        context['kernel_image'] = image_get(
            self.request,
            context['flavor'].kernel_image_id,
            error_message=_("Cannot get kernel image details")
        )
        context['ramdisk_image'] = image_get(
            self.request,
            context['flavor'].ramdisk_image_id,
            error_message=_("Cannot get ramdisk image details")
        )
        return context

    def get_data(self):
        return [role for role in tuskar_ui.api.OvercloudRole.list(self.request)
                if role.flavor_id == str(self.kwargs.get('flavor_id'))]
