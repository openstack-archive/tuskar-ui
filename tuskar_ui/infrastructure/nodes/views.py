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

from openstack_dashboard.test.test_data import utils

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms
from tuskar_ui.infrastructure.nodes import tabs
from tuskar_ui.test.test_data import tuskar_data


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
        # TODO(akrivoka): replace mocked data with real data from Ceilometer
        TEST_DATA = utils.TestDataContainer()
        tuskar_data.data(TEST_DATA)
        ceilometer_data = TEST_DATA.ceilometer.first()

        meter = request.GET.get('meter', None)

        values = [c['value'] for c in ceilometer_data]
        first_date = ceilometer_data[0]['date']
        last_date = ceilometer_data[-1]['date']
        average = sum(values)/len(values)
        used = values[-1]
        tooltip_average = 'Average %s &percnt;<br> From: %s, to: %s' % (
            average, first_date.isoformat(), last_date.isoformat())

        capacity_data = {
            'series': [
                {
                    'data': [
                        {'y': c['value'], 'x': c['date'].isoformat()}
                        for c in ceilometer_data
                    ],
                    'name': meter.capitalize(),
                    'unit': '%'
                }
            ],
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
                'tooltip_average': tooltip_average
            }
        }

        return http.HttpResponse(json.dumps(capacity_data),
                                 mimetype='application/json')
