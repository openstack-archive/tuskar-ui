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

from datetime import datetime
from datetime import timedelta
import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from horizon import exceptions
from horizon import forms
from horizon import tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure. \
    resource_management.flavors.forms import CreateFlavor
from tuskar_ui.infrastructure. \
    resource_management.flavors.forms import EditFlavor
from tuskar_ui.infrastructure. \
    resource_management.flavors.tabs import FlavorDetailTabs


LOG = logging.getLogger(__name__)


class CreateView(forms.ModalFormView):
    form_class = CreateFlavor
    template_name = 'infrastructure/resource_management/flavors/create.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')


class EditView(forms.ModalFormView):
    form_class = EditFlavor
    template_name = 'infrastructure/resource_management/flavors/edit.html'
    form_url = 'horizon:infrastructure:resource_management:flavors:edit'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        context['flavor_id'] = self.kwargs['flavor_id']
        context['form_url'] = self.form_url
        context['success_url'] = self.get_success_url()
        return context

    def get_initial(self):
        try:
            flavor = tuskar.FlavorTemplate.get(
                self.request, self.kwargs['flavor_id'])
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve flavor data."))
        return {'flavor_id': flavor.id,
                'name': flavor.name,
                'cpu': flavor.cpu.value,
                'memory': flavor.memory.value,
                'storage': flavor.storage.value,
                'ephemeral_disk': flavor.ephemeral_disk.value,
                'swap_disk': flavor.swap_disk.value}


class DetailEditView(EditView):
    form_url = 'horizon:infrastructure:resource_management:flavors:detail_edit'
    success_url = 'horizon:infrastructure:resource_management:flavors:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['flavor_id'],))


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
                flavor = tuskar.FlavorTemplate.get(self.request, flavor_id)
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


class ActiveInstancesDataView(View):

    def get(self, request, *args, **kwargs):
        try:
            flavor = tuskar.FlavorTemplate.get(
                self.request, self.kwargs['flavor_id'])
            values = flavor.vms_over_time(
                datetime.now() - timedelta(days=7), datetime.now())
            return HttpResponse(json.dumps(values, cls=DjangoJSONEncoder),
                                mimetype='application/json')
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve flavor data."))
