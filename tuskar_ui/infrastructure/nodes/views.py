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

from datetime import datetime  # noqa
from datetime import timedelta  # noqa
from django.utils import timezone

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
from openstack_dashboard.api import ceilometer

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
            query = [{'field': 'resource_id',
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
                resources, unit = query_data(
                    request=request,
                    date_from=date_from,
                    date_to=date_to,
                    date_options=date_options,
                    group_by=group_by,
                    meter=meter_id,
                    query=query)
                next_series = metering.SamplesView._series_for_meter(
                    resources,
                    resource_name,
                    meter_name,
                    stats_attr,
                    unit)
                # You would think the meter name would be a part of the
                # returned data...
                for serie in next_series:
                    serie['meter'] = meter_id
                series.extend(next_series)

            if meter == 'swap-util':
                # Divide available swap with used swap, multiply by 100.
                # Integers are good enough here.
                for serie in series:
                    if serie['meter'] == 'hardware.memory.swap.util':
                        util = serie.copy()
                    if serie['meter'] == 'hardware.memory.swap.total':
                        total = serie.copy()

                for i, d in enumerate(util['data']):
                    try:
                        util['data'][i]['y'] =\
                            int((100*d['y'])//total['data'][i]['y'])
                    except IndexError:
                        # Could happen if one series is shorter.
                        del util['data'][i]
                util['unit'] = '%'
                series = [util]

            if not series:
                barchart = False
            if barchart:
                average, used, tooltip_average = get_barchart_stats(series,
                                                                    unit)

        json_output = create_json_output(series)

        if barchart:
            json_output = add_barchart_settings(json_output, average, used,
                                                tooltip_average)

        return http.HttpResponse(json.dumps(json_output),
                                 mimetype='application/json')


#TODO(lsmola) this should probably live in Horizon common
def query_data(request,
               date_from,
               date_to,
               date_options,
               group_by,
               meter,
               period=None,
               query=None,
               additional_query=None):
    date_from, date_to = _calc_date_args(date_from,
                                         date_to,
                                         date_options)
    if not period:
        period = _calc_period(date_from, date_to, 20)
    if additional_query is None:
        additional_query = []
    if date_from:
        additional_query += [{'field': 'timestamp',
                              'op': 'ge',
                              'value': date_from}]
    if date_to:
        additional_query += [{'field': 'timestamp',
                              'op': 'le',
                              'value': date_to}]

    # TODO(lsmola) replace this by logic implemented in I1 in bugs
    # 1226479 and 1226482, this is just a quick fix for RC1
    try:
        meter_list = [m for m in metering.meter_list(request)
                      if m.name == meter]
        unit = meter_list[0].unit
    except Exception:
        unit = ""
    if group_by == "resources":
        # TODO(lsmola) need to implement group_by groups of resources
        resources = []
        unit = ""
    else:
        ceilometer_usage = ceilometer.CeilometerUsage(request)
        try:
            resources = ceilometer_usage.resources_with_statistics(
                query, [meter], period=period, stats_attr=None,
                additional_query=additional_query)
        except Exception:
            resources = []
            exceptions.handle(request,
                              _('Unable to retrieve statistics.'))
    return resources, unit


#TODO(lsmola) push this function to Horizon common then delete this
def _calc_period(date_from, date_to, number_of_samples=400):
    if date_from and date_to:
        if date_to < date_from:
            # TODO(lsmola) propagate the Value error through Horizon
            # handler to the client with verbose message.
            raise ValueError("Date to must be bigger than date "
                             "from.")
            # get the time delta in seconds
        delta = date_to - date_from
        delta_in_seconds = delta.days * 24 * 3600 + delta.seconds

        period = delta_in_seconds / number_of_samples
    else:
        # If some date is missing, just set static window to one day.
        period = 3600 * 24
    return period


#TODO(lsmola) push this function to Horizon common then delete this
def _calc_date_args(date_from, date_to, date_options):
    # TODO(lsmola) all timestamps should probably work with
    # current timezone. And also show the current timezone in chart.
    if date_options == "other":
        try:
            if date_from:
                date_from = datetime.strptime(date_from,
                                              "%Y-%m-%d")
            else:
                # TODO(lsmola) there should be probably the date
                # of the first sample as default, so it correctly
                # counts the time window. Though I need ordering
                # and limit of samples to obtain that.
                pass
            if date_to:
                date_to = datetime.strptime(date_to,
                                            "%Y-%m-%d")
                # It return beginning of the day, I want the and of
                # the day, so i will add one day without a second.
                date_to = (date_to + timedelta(days=1) -
                           timedelta(seconds=1))
            else:
                date_to = timezone.now()
        except Exception:
            raise ValueError("The dates haven't been "
                             "recognized")
    else:
        try:
            date_from = timezone.now() - timedelta(days=float(date_options))
            date_to = timezone.now()
        except Exception:
            raise ValueError("The time delta must be an "
                             "integer representing days.")
    return date_from, date_to


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
