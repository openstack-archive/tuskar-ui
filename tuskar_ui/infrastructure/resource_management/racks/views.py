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

import datetime
import json
import logging
import random

from django.core.serializers import json as json_serializer
from django.core import urlresolvers
from django import http

from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _  # noqa
from django.views import generic

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management.racks import forms
from tuskar_ui.infrastructure.resource_management.racks import tables
from tuskar_ui.infrastructure.resource_management.racks import tabs
from tuskar_ui.infrastructure.resource_management.racks import workflows
from tuskar_ui import workflows as tuskar_workflows


LOG = logging.getLogger(__name__)


class CreateView(tuskar_workflows.WorkflowView):
    workflow_class = workflows.CreateRack

    def get_initial(self):
        pass


class UploadView(horizon_forms.ModalFormView):
    form_class = forms.UploadRack
    template_name = 'infrastructure/resource_management/racks/upload.html'
    success_url = urlresolvers.reverse_lazy(
        'horizon:infrastructure:resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        context['racks_table'] = tables.UploadRacksTable(
            self.request, kwargs['form'].initial.get('racks', []))
        return context


class EditView(tuskar_workflows.WorkflowView):
    workflow_class = workflows.EditRack

    def get_initial(self):
        obj = tuskar.Rack.get(self.request, self.kwargs['rack_id'])
        # mac_str = "\n".join(x.mac_address for x in obj.list_tuskar_nodes)
        return {'name': obj.name, 'resource_class_id': obj.resource_class_id,
                'location': obj.location, 'subnet': obj.subnet,
                'state': obj.state, 'rack_id': self.kwargs['rack_id']}


class DetailEditView(EditView):
    workflow_class = workflows.DetailEditRack


class EditRackStatusView(horizon_forms.ModalFormView):
    form_class = forms.UpdateRackStatus
    template_name = 'infrastructure/resource_management/racks/edit_status.html'

    def get_success_url(self):
        # Redirect to previous url
        default_url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:index')
        return self.request.META.get('HTTP_REFERER', default_url)

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


class DetailView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.RackDetailTabs
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
                redirect = urlresolvers.reverse(
                    'horizon:infrastructure:resource_management:index')
                exceptions.handle(
                    self.request,
                    _('Unable to retrieve details for rack "%s".') % rack_id,
                    redirect=redirect)
            self._rack = rack
        return self._rack

    def get_tabs(self, request, *args, **kwargs):
        rack = self.get_data()
        return self.tab_group_class(request, rack=rack,
                                    **kwargs)


class UsageDataView(generic.View):

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
            timediff = datetime.timedelta(**{timedelta_param: i})
            current_value = {'date': datetime.datetime.now() - timediff}

            for usage_type in series:
                current_value[usage_type] = random.randint(1, 9)

            values.append(current_value)

        return http.HttpResponse(
            json.dumps(values, cls=json_serializer.DjangoJSONEncoder),
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
    for tuskar_node_id in rack.tuskar_node_ids:
        status = random.randint(0, 3)
        percentage = random.randint(0, 100)

        tooltip = ("<p>Node: <strong>{0}</strong></p><p>{1}</p>").format(
            tuskar_node_id, statuses[status])

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
    return http.HttpResponse(simplejson.dumps(res),
                             mimetype="application/json")


def node_health(request, rack_id=None):
    # FIXME replace mock data
    random.seed()
    data = []
    statuses = ["Good", "Warnings", "Disaster"]
    colors = ["rgb(244,244,244)", "rgb(240,170,0)", "rgb(200,0,0)"]

    rack = tuskar.Rack.get(request, rack_id)

    for tuskar_node_id in rack.tuskar_node_ids:
        rand_index = random.randint(0, 2)
        percentage = (2 - rand_index) * 50
        color = colors[rand_index]

        tooltip = ("<p>Node: <strong>{0}</strong></p><p>{1}</p>").format(
            tuskar_node_id, statuses[rand_index])

        data.append({'tooltip': tooltip,
                     'color': color,
                     'status': statuses[rand_index],
                     'percentage': percentage,
                     'id': tuskar_node_id,
                     'name': tuskar_node_id,
                     'url': "FIXME url"})

        data.sort(key=lambda x: x['percentage'])

    res = {'data': data}
    return http.HttpResponse(simplejson.dumps(res),
                             mimetype="application/json")


def check_state(request, rack_id=None):
    rack = tuskar.Rack.get(request, rack_id)

    res = {'state': rack.state}

    return http.HttpResponse(simplejson.dumps(res),
                             mimetype="application/json")
