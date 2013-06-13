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

from openstack_dashboard import api
from .forms import CreateFlavor, EditFlavor
from .tables import FlavorsTable


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
        context['flavor_id'] = self.kwargs['id']
        return context

    def get_initial(self):
        try:
            flavor = api.management.Flavor.get(
                self.request, self.kwargs['id'])
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve flavor data."))
        return {'flavor_id': flavor.id,
                'name': flavor.name}
