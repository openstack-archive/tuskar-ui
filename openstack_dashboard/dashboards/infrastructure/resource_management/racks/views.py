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
from horizon import tabs
from horizon import forms
from horizon import workflows
from .workflows import (CreateRack, EditRack)

from openstack_dashboard import api

from .forms import UploadRack
from .tabs import RackDetailTabs
from .tables import UploadRacksTable


LOG = logging.getLogger(__name__)


class CreateView(workflows.WorkflowView):
    workflow_class = CreateRack

    def get_initial(self):
        pass


class UploadView(forms.ModalFormView):
    form_class = UploadRack
    template_name = 'infrastructure/resource_management/racks/upload.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        context['racks_table'] = UploadRacksTable(
                self.request, kwargs['form'].initial.get('racks', []))
        return context


class EditView(workflows.WorkflowView):
    workflow_class = EditRack

    def get_initial(self):
        obj = api.management.Rack.get(None,
                                      rack_id=self.kwargs['rack_id'])
        mac_str = "\n".join([x.mac_address for x in obj.nodes])
        return {'name': obj.name, 'resource_class_id': obj.resource_class_id,
                'location': obj.location, 'subnet': obj.subnet,
                'node_macs': mac_str, 'rack_id': self.kwargs['rack_id']}


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
        interval = request.GET.get('interval', '1w')

        if interval == '12h':
            data_count = 12
            timedelta_param = 'hours'
        elif interval == '24h':
            data_count = 24
            timedelta_param = 'hours'
        elif interval == '1m':
            data_count = 30
            timedelta_param = 'days'
        elif interval == '1y':
            data_count = 52
            timedelta_param = 'weeks'
        else:
            # default is 1 week
            data_count = 7
            timedelta_param = 'days'

        values = []
        for i in range(data_count):
            timediff = timedelta(**{timedelta_param: i})
            values.append({'date': datetime.now() - timediff,
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
