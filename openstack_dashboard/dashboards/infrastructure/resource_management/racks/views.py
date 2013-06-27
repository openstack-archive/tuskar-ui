# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from datetime import datetime, timedelta
import json
import logging
import random

from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse

from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from horizon import exceptions
from horizon import forms
from horizon import tabs

from openstack_dashboard import api
from .forms import CreateRack, EditRack
from .tabs import RackDetailTabs


LOG = logging.getLogger(__name__)


class CreateView(forms.ModalFormView):
    form_class = CreateRack
    template_name = 'infrastructure/resource_management/racks/create.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')


class EditView(forms.ModalFormView):
    form_class = EditRack
    template_name = 'infrastructure/resource_management/racks/edit.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        context['rack_id'] = self.kwargs['rack_id']
        return context

    def get_initial(self):
        try:
            rack = api.management.Rack.get(self.request,
                                           self.kwargs['rack_id'])
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve rack data."))
        return {'rack_id': rack.id,
                'name': rack.name,
                'resource_class_id': rack.resource_class_id,
                'location': rack.location,
                'subnet': rack.subnet}


class DetailView(tabs.TabView):
    tab_group_class = RackDetailTabs
    template_name = 'infrastructure/resource_management/racks/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["rack"] = self.get_data()
        return context

    def get_data(self):
        if not hasattr(self, "_rack"):
            try:
                rack_id = self.kwargs['rack_id']
                rack = api.management.Rack.get(self.request, rack_id)
            except:
                redirect = reverse('horizon:infrastructure:'
                                   'resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'rack "%s".')
                                    % rack_id,
                                    redirect=redirect)
            self._rack = rack
        return self._rack

    def get_tabs(self, request, *args, **kwargs):
        rack = self.get_data()
        return self.tab_group_class(request, rack=rack,
                                    **kwargs)


class UsageDataView(View):

    def get(self, request, *args, **kwargs):
        values = []
        for i in range(10):
            values.append({'date': datetime.now() + timedelta(days=i),
                           'ram': random.randint(1, 9)})

        return HttpResponse(json.dumps(values, cls=DjangoJSONEncoder),
                            mimetype='application/json')


def top_communicating(request, rack_id=None):
    random.seed()
    data = []
    statuses = ["OFF", "Good", "Something is wrong", "Disaster"]

    number_of_elements = random.randint(50, 60)
    for index in range(number_of_elements):
        status = random.randint(0, 3)
        percentage = random.randint(0, 100)

        # count black/white color depending to percentage
        # FIXME encapsulate the algoritm of getting color to the library,
        # If the algorithm will be used in multiple places. Then pass the
        # alghoritm name and parameters.
        # If it will be used only in one place, pass the color directly.
        color_n = 255 / 100 * percentage
        color = "rgb(%s, %s, %s)" % (color_n, color_n, color_n)

        data.append({'color': color,
                     'status': statuses[status],
                     'percentage': percentage,
                     'id': "FIXME_RACK id",
                     'name': "FIXME name",
                     'url': "FIXME url"})

        data.sort(key=lambda x: x['percentage'])

    return HttpResponse(simplejson.dumps(data),
        mimetype="application/json")
