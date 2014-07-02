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

    def get_free_nodes_count(self):
        free_nodes_count = len(api.node.Node.list(
            self.request, associated=False))
        return free_nodes_count

    def get_deployed_nodes_count(self):
        deployed_nodes_count = len(api.node.Node.list(self.request,
                                                      associated=True))
        return deployed_nodes_count

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['free_nodes_count'] = self.get_free_nodes_count()
        context['deployed_nodes_count'] = self.get_deployed_nodes_count()
        context['nodes_count'] = (context['free_nodes_count'] +
                                  context['deployed_nodes_count'])

        return context


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
        try:
            resource = api.heat.Resource.get_by_node(request, node)
            context['role'] = resource.role
            context['stack'] = resource.stack
        except exceptions.NotFound:
            pass
        if api_base.is_service_enabled(request, 'metering'):
            # Meter configuration in the following format:
            # (meter label, url part)
            context['meter_conf'] = (
                # CPU load
                (_('CPU load average (1 min)'),
                 url_part('hardware.cpu.load.1min', False)),
                # CPU utilization
                (_('CPU utilization'),
                 url_part('hardware.system_stats.cpu.util', True)),
                # Swap
                # TODO(akrivoka): Both lines in one chart, with barchart.
                (_('Swap (total)'),
                 url_part('hardware.memory.swap.total', False)),
                (_('Swap (used)'),
                 url_part('hardware.memory.swap.util', False)),
                # Disk
                (_('Disk I/O (out)'),
                 url_part('hardware.system_stats.io.raw_sent', False)),
                (_('Disk I/O (in)'),
                 url_part('hardware.system_stats.io.raw_received', False)),
                # Network
                (_('Network bandwidth (out)'),
                 url_part('hardware.network.ip.out_requests', False)),
                (_('Network bandwidth (in)'),
                 url_part('hardware.network.ip.in_receives', False)),
            )

        return context


def url_part(meter_name, barchart):
    d = {'meter': meter_name}
    if barchart:
        d['barchart'] = True
    return urlencode(d)


class PerformanceView(base.TemplateView):
    def get(self, request, *args, **kwargs):
        meter = request.GET.get('meter')
        date_options = request.GET.get('date_options')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        stats_attr = request.GET.get('stats_attr', 'avg')
        group_by = request.GET.get('group_by')
        barchart = bool(request.GET.get('barchart'))

        meter_name = meter.replace(".", "_")
        resource_name = 'id' if group_by == "project" else 'resource_id'
        node_uuid = kwargs.get('node_uuid')
        node = api.node.Node.get(request, node_uuid)

        average = used = 0
        tooltip_average = ''

        try:
            ip_addr = node.driver_info['ip_address']
        except AttributeError:
            series = []
        else:
            additional_query = [{'field': 'resource_id',
                                 'op': 'eq',
                                 'value': ip_addr}]
            resources, unit = metering.query_data(
                request=request,
                date_from=date_from,
                date_to=date_to,
                date_options=date_options,
                group_by=group_by,
                meter=meter,
                additional_query=additional_query)
            series = metering.SamplesView._series_for_meter(resources,
                                                            resource_name,
                                                            meter_name,
                                                            stats_attr,
                                                            unit)

            if barchart:
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

        ret = {
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

        if barchart:
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

        return http.HttpResponse(json.dumps(ret), mimetype='application/json')
