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
import json

from django.core.urlresolvers import reverse_lazy
from django import http
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs
from horizon import views as horizon_views

from openstack_dashboard.api import base as api_base
from openstack_dashboard.dashboards.admin.metering import views as metering

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms
from tuskar_ui.infrastructure.nodes import tabs


class IndexView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.NodeTabs
    template_name = 'infrastructure/nodes/index.html'


class RegisterView(horizon_forms.ModalFormView):
    form_class = forms.NodeFormset
    form_prefix = 'register_nodes'
    template_name = 'infrastructure/nodes/register.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:nodes:index')

    def get_data(self):
        return []

    def get_form(self, form_class):
        return form_class(self.request.POST or None,
                          initial=self.get_data(),
                          prefix=self.form_prefix)


class DetailView(horizon_views.APIView):
    template_name = 'infrastructure/nodes/details.html'

    def get_data(self, request, context, *args, **kwargs):
        node_uuid = kwargs.get('node_uuid')
        redirect = reverse_lazy('horizon:infrastructure:nodes:index')
        node = api.node.Node.get(request, node_uuid, _error_redirect=redirect)
        context['node'] = node
        context['title'] = _("Node Details: %(uuid)s") % {'uuid': node.uuid}
        try:
            resource = api.heat.Resource.get_by_node(request, node)
            context['role'] = resource.role
            context['stack'] = resource.stack
        except exceptions.NotFound:
            pass
        if node.instance_uuid:
            if api_base.is_service_enabled(request, 'metering'):
                # Meter configuration in the following format:
                # (meter label, url part, barchart (True/False))
                context['meter_conf'] = (
                    (_('System Load'),
                     url_part('hardware.cpu.load.1min', False),
                     None),
                    (_('CPU Utilization'),
                     url_part('hardware.system_stats.cpu.util', True),
                     '100'),
                    (_('Swap Utilization'),
                     url_part('swap-util', True),
                     '100'),
                    (_('Disk I/O '),
                     url_part('disk-io', False),
                     None),
                    (_('Network I/O '),
                     url_part('network-io', False),
                     None),
                )
        return context


class PerformanceView(base.TemplateView):
    def get(self, request, *args, **kwargs):
        meter = request.GET.get('meter')
        date_options = request.GET.get('date_options')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        stats_attr = request.GET.get('stats_attr', 'avg')
        group_by = request.GET.get('group_by')
        barchart = bool(request.GET.get('barchart'))

        resource_name = 'id' if group_by == "project" else 'resource_id'
        node_uuid = kwargs.get('node_uuid')
        node = api.node.Node.get(request, node_uuid)

        average = used = 0
        tooltip_average = ''
        series = []

        try:
            ip_addr = node.driver_info['ip_address']
        except AttributeError:
            pass
        else:
            additional_query = [{'field': 'resource_id',
                                 'op': 'eq',
                                 'value': ip_addr}]

            # Disk and Network I/O: data from 2 meters in one chart
            if meter == 'disk-io':
                meters = get_meters([
                    'hardware.system_stats.io.raw_sent',
                    'hardware.system_stats.io.raw_received'
                ])
            elif meter == 'network-io':
                meters = get_meters([
                    'hardware.network.ip.out_requests',
                    'hardware.network.ip.in_receives'
                ])
            elif meter == 'swap-util':
                meters = get_meters([
                    'hardware.memory.swap.util',
                    'hardware.memory.swap.total'
                ])
            else:
                meters = get_meters([meter])

            for meter_id, meter_name in meters:
                resources, unit = metering.query_data(
                    request=request,
                    date_from=date_from,
                    date_to=date_to,
                    date_options=date_options,
                    group_by=group_by,
                    meter=meter_id,
                    additional_query=additional_query)
                series.extend(metering.SamplesView._series_for_meter(
                    resources,
                    resource_name,
                    meter_name,
                    stats_attr,
                    unit))
            if meter == 'swap-util':
                data = []
                # Divide available swap with used swap, multiply by 100.
                # Integers are good enough here.
                result = series[0].copy()

                for i, d in enumerate(result['data']):
                    try:
                        result['data'][i]['y'] = int((100*series[0]['data'][i]['y'])//series[2]['data'][i]['y'])
                    except IndexError:
                        # Could happen if one series is shorter.
                        del result['data'][i]
                result['unit'] = '%'
                series = [result]

            if barchart:
                average, used, tooltip_average = get_barchart_stats(series,
                                                                    unit)

        json_output = create_json_output(series)

        if barchart:
            json_output = add_barchart_settings(json_output, average, used,
                                                tooltip_average)

        return http.HttpResponse(json.dumps(json_output),
                                 mimetype='application/json')


def url_part(meter_name, barchart):
    d = {'meter': meter_name}
    if barchart:
        d['barchart'] = True
    return urlencode(d)


def get_meter_name(meter):
    return meter.replace('.', '_')


def get_meters(meters):
    return [(m, get_meter_name(m)) for m in meters]


def get_barchart_stats(series, unit):
    values = [point['y'] for point in series[0]['data']]
    average = sum(values) / len(values)
    used = values[-1]
    first_date = series[0]['data'][0]['x']
    last_date = series[0]['data'][-1]['x']
    tooltip_average = _('Average %(average)s %(unit)s<br> From: '
                        '%(first_date)s, to: %(last_date)s') % (
                            dict(average=average, unit=unit,
                                 first_date=first_date,
                                 last_date=last_date)
                        )
    return average, used, tooltip_average


def create_json_output(series):
    return {
        'series': series,
        'settings': {
            'renderer': 'StaticAxes',
            'yMin': 0,
            'higlight_last_point': True,
            'auto_size': False,
            'auto_resize': False,
            'axes_x': False,
            'axes_y': True,
        },
    }


def add_barchart_settings(ret, average, used, tooltip_average):
    ret['settings']['bar_chart_settings'] = {
        'orientation': 'vertical',
        'used_label_placement': 'left',
        'width': 30,
        'color_scale_domain': [0, 80, 80, 100],
        'color_scale_range': [
            '#0000FF',
            '#0000FF',
            '#FF0000',
            '#FF0000'
        ],
        'average_color_scale_domain': [0, 100],
        'average_color_scale_range': ['#0000FF', '#0000FF']
    }
    ret['stats'] = {
        'average': average,
        'used': used,
        'tooltip_average': tooltip_average,
    }
    return ret
