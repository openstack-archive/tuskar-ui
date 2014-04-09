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
from django.views.generic import base

from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs
from horizon import views as horizon_views

from openstack_dashboard.dashboards.admin.metering import views \
    as metering_views

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms
from tuskar_ui.infrastructure.nodes import tabs


class IndexView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.NodeTabs
    template_name = 'infrastructure/nodes/index.html'

    def get_free_nodes_count(self):
        free_nodes_count = len(api.Node.list(self.request, associated=False))
        return free_nodes_count

    def get_deployed_nodes_count(self):
        deployed_nodes_count = len(api.Node.list(self.request,
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
        node = api.Node.get(request, node_uuid, _error_redirect=redirect)
        context['node'] = node
        return context


class PerformanceView(base.TemplateView):
    def get(self, request, *args, **kwargs):
        meter = request.GET.get('meter', None)
        if not meter:
            return http.HttpResponse(json.dumps({}),
                                     content_type='application/json')

        meter_name = meter.replace(".", "_")
        date_options = request.GET.get('date_options', None)
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)
        stats_attr = request.GET.get('stats_attr', 'avg')
        group_by = request.GET.get('group_by', None)

        resource_name = 'id' if group_by == "project" else 'resource_id'

        # TODO(akrivoka): Delete when Ceilometer integration is in
        import datetime
        import random
        n = 20
        dates = [datetime.datetime(2014, 3, day, 3, 14, 15).isoformat()
                 for day in xrange(1, n+1)]
        values = [random.randint(0, 100) for r in xrange(n)]
        data = [dict(x=d, y=values[i]) for i, d in enumerate(dates)]
        unit = '%'
        series = [{
            'name': meter_name,
            'unit': unit,
            'data': data,
        }]

        # TODO(akrivoka): Uncomment when Ceilometer integration is in
        # resources, unit = metering_views.query_data(request,
        #                                             date_from,
        #                                             date_to,
        #                                             date_options,
        #                                             group_by,
        #                                             meter)
        #
        # series = metering_views.SamplesView._series_for_meter(resources,
        #                                                       resource_name,
        #                                                       meter_name,
        #                                                       stats_attr,
        #                                                       unit)

        values = [point['y'] for point in series[0]['data']]
        average = sum(values) / len(values)
        used = values[-1]
        first_date = series[0]['data'][0]['x']
        last_date = series[0]['data'][-1]['x']
        tooltip_average = 'Average %s %s<br> From: %s, to: %s' % (
            average, unit, first_date, last_date)

        ret = {
            'series': series,
            'settings': {
                'renderer': 'StaticAxes',
                'yMin': 0,
                'yMax': 100,
                'higlight_last_point': True,
                'auto_size': False,
                'auto_resize': False,
                'axes_x': False,
                'axes_y': False,
                'bar_chart_settings': {
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
            },
            'stats': {
                'average': average,
                'used': used,
                'tooltip_average': tooltip_average,
            }
        }

        return http.HttpResponse(json.dumps(ret), mimetype='application/json')
