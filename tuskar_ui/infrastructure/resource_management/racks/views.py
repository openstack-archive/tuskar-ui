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

from datetime import datetime
from datetime import timedelta
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
from horizon import workflows

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure. \
    resource_management.racks.forms import UpdateRackStatus
from tuskar_ui.infrastructure. \
    resource_management.racks.forms import UploadRack
from tuskar_ui.infrastructure. \
    resource_management.racks.tabs import RackDetailTabs
from tuskar_ui.infrastructure. \
    resource_management.racks.tables import UploadRacksTable
from tuskar_ui.infrastructure. \
    resource_management.racks.workflows import CreateRack
from tuskar_ui.infrastructure. \
    resource_management.racks.workflows import DetailEditRack
from tuskar_ui.infrastructure. \
    resource_management.racks.workflows import EditRack


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
        obj = tuskar.Rack.get(self.request, self.kwargs['rack_id'])
        # mac_str = "\n".join([x.mac_address for x in obj.list_nodes])
        return {'name': obj.name, 'resource_class_id': obj.resource_class_id,
                'location': obj.location, 'subnet': obj.subnet,
                'state': obj.state, 'rack_id': self.kwargs['rack_id']}


class DetailEditView(EditView):
    workflow_class = DetailEditRack


class EditRackStatusView(forms.ModalFormView):
    form_class = UpdateRackStatus
    template_name = 'infrastructure/resource_management/racks/edit_status.html'

    def get_success_url(self):
        # Redirect to previous url
        return self.request.META.get('HTTP_REFERER', None)

    def get_context_data(self, **kwargs):
        context = super(EditRackStatusView, self).get_context_data(**kwargs)
        context['rack_id'] = self.kwargs['rack_id']
        context['action'] = context['form'].initial.get('action', None)
        return context

    def get_initial(self):
        try:
            rack = tuskar.Rack.get(
                self.request, self.kwargs['rack_id'])
            action = self.request.GET.get('action')
        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve rack data."))
        return {'rack': rack,
                'action': action}


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
                rack = tuskar.Rack.get(self.request, rack_id)
            except Exception:
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
        series = request.GET.get('series', "")
        series = series.split(',')

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
            current_value = {'date': datetime.now() - timediff}

            for usage_type in series:
                current_value[usage_type] = random.randint(1, 9)

            values.append(current_value)

        return HttpResponse(json.dumps(values, cls=DjangoJSONEncoder),
                            mimetype='application/json')


def top_communicating(request, rack_id=None):
    # FIXME replace mock data
    random.seed()
    data = []
    statuses = ["Insane level of communication",
                "High level of communication",
                "Normal level of communication",
                "Low level of communication"]

    rack = tuskar.Rack.get(request, rack_id)
    for node in rack.nodes:
        status = random.randint(0, 3)
        percentage = random.randint(0, 100)

        tooltip = ("<p>Node: <strong>{0}</strong></p><p>{1}</p>").format(
            node['id'],
            statuses[status])

        data.append({'tooltip': tooltip,
                     'status': statuses[status],
                     'scale': 'linear_color_scale',
                     'percentage': percentage,
                     'id': "FIXME_RACK id",
                     'name': "FIXME name",
                     'url': "FIXME url"})

        data.sort(key=lambda x: x['percentage'])

    # FIXME dynamically set the max domain, based on data
    settings = {'scale': 'linear_color_scale',
                'domain': [0, max([datum['percentage'] for datum in data])],
                'range': ["#000060", "#99FFFF"]}
    res = {'data': data,
           'settings': settings}
    return HttpResponse(simplejson.dumps(res),
        mimetype="application/json")


def node_health(request, rack_id=None):
    # FIXME replace mock data
    random.seed()
    data = []
    statuses = ["Good", "Warnings", "Disaster"]
    colors = ["rgb(244,244,244)", "rgb(240,170,0)", "rgb(200,0,0)"]

    rack = tuskar.Rack.get(request, rack_id)

    for node in rack.nodes:
        rand_index = random.randint(0, 2)
        percentage = (2 - rand_index) * 50
        color = colors[rand_index]

        tooltip = ("<p>Node: <strong>{0}</strong></p><p>{1}</p>").format(
            node['id'],
            statuses[rand_index])

        data.append({'tooltip': tooltip,
                     'color': color,
                     'status': statuses[rand_index],
                     'percentage': percentage,
                     'id': node['id'],
                     'name': node['id'],
                     'url': "FIXME url"})

        data.sort(key=lambda x: x['percentage'])

    res = {'data': data}
    return HttpResponse(simplejson.dumps(res),
        mimetype="application/json")


def check_state(request, rack_id=None):
    rack = tuskar.Rack.get(request, rack_id)

    res = {'state': rack.state}

    return HttpResponse(
        simplejson.dumps(res),
        mimetype="application/json")
