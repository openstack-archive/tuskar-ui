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
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.tables
import horizon.tabs
from horizon.utils import memoized
import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.flavors import tables
from tuskar_ui.infrastructure.flavors import utils
from tuskar_ui.infrastructure.flavors import workflows


class IndexView(horizon.tables.MultiTableView):
    table_classes = (tables.FlavorsTable, tables.FlavorSuggestionsTable)
    template_name = 'infrastructure/flavors/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        create_action = {
            'name': _("New Flavor"),
            'url': reverse('horizon:infrastructure:flavors:create'),
            'icon': 'fa-plus',
        }
        context['header_actions'] = [create_action]
        context['flavors_count'] = self.get_flavors_count()
        context['suggested_flavors_count'] = self.get_suggested_flavors_count()
        return context

    @memoized.memoized_method
    def get_flavors_data(self):
        flavors = api.flavor.Flavor.list(self.request)
        flavors.sort(key=lambda np: (np.vcpus, np.ram, np.disk))
        return flavors

    @memoized.memoized_method
    def get_suggested_flavors_data(self):
        return list(utils.get_flavor_suggestions(self.request))

    def get_flavors_count(self):
        return len(self.get_flavors_data())

    def get_suggested_flavors_count(self):
        return len(self.get_suggested_flavors_data())


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = workflows.CreateFlavor
    template_name = 'infrastructure/flavors/create.html'

    def get_initial(self):
        suggestion_id = self.kwargs.get('suggestion_id')
        if not suggestion_id:
            return super(CreateView, self).get_initial()
        node = api.node.Node.get(self.request, suggestion_id)
        suggestion = utils.FlavorSuggestion.from_node(node)
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
        context['flavor'] = api.flavor.Flavor.get(
            self.request,
            kwargs.get('flavor_id'),
            _error_redirect=self.error_redirect
        )
        context['kernel_image'] = api.node.image_get(
            self.request,
            context['flavor'].kernel_image_id
        )
        context['ramdisk_image'] = api.node.image_get(
            self.request,
            context['flavor'].ramdisk_image_id
        )
        return context

    def get_data(self):
        flavor_id = self.kwargs.get('flavor_id')
        plan = api.tuskar.Plan.get_the_plan(self.request)

        return [role for role in api.tuskar.Role.list(self.request)
                if role.flavor(plan).id == flavor_id]
