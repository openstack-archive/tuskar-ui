# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs

from openstack_dashboard import api
from .forms import CreateFlavor, EditFlavor
from .tables import FlavorsTable
from .tabs import FlavorDetailTabs


LOG = logging.getLogger(__name__)


class CreateView(forms.ModalFormView):
    form_class = CreateFlavor
    template_name = 'infrastructure/resource_management/flavors/create.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')


class EditView(forms.ModalFormView):
    form_class = EditFlavor
    template_name = 'infrastructure/resource_management/flavors/edit.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        context['flavor_id'] = self.kwargs['flavor_id']
        return context

    def get_initial(self):
        try:
            flavor = api.management.Flavor.get(
                self.request, self.kwargs['flavor_id'])
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve flavor data."))
        return {'flavor_id': flavor.id,
                'name': flavor.name,
                'vcpu': flavor.vcpu.value,
                'ram': flavor.ram.value,
                'root_disk': flavor.root_disk.value,
                'ephemeral_disk': flavor.ephemeral_disk.value,
                'swap_disk': flavor.swap_disk.value}


class DetailView(tabs.TabView):
    tab_group_class = FlavorDetailTabs
    template_name = 'infrastructure/resource_management/flavors/detail.html'

    def get_context_data(self, **kwargs):
            context = super(DetailView, self).get_context_data(**kwargs)
            context["flavor"] = self.get_data()
            return context

    def get_data(self):
        if not hasattr(self, "_flavor"):
            try:
                flavor_id = self.kwargs['flavor_id']
                flavor = api.management.Flavor.get(self.request, flavor_id)
            except:
                redirect = reverse('horizon:infrastructure:'
                                   'resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'flavor "%s".')
                                    % flavor_id,
                                    redirect=redirect)
            self._flavor = flavor
        return self._flavor

    def get_tabs(self, request, *args, **kwargs):
        flavor = self.get_data()
        return self.tab_group_class(request, flavor=flavor,
                                    **kwargs)
