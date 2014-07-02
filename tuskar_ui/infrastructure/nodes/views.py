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
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base

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

        if api_base.is_service_enabled(request, 'metering'):
            context['meters'] = (
                ('hardware.cpu.load.15min', _('CPU load (15 min)')),
                ('hardware.disk.size.total', _('Disk size (total)')),
                ('hardware.disk.size.used', _('Disk size (used)')),
                ('hardware.memory.total', _('Memory (total)')),
                ('hardware.memory.used', _('Memory (used)')),
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

        meter_name = meter.replace(".", "_")
        resource_name = 'id' if group_by == "project" else 'resource_id'
        node_uuid = kwargs.get('node_uuid')
        node = api.node.Node.get(request, node_uuid)
        ip_addr = node.instance._apiresource.addresses['ctlplane'][0]['addr']

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

        return http.HttpResponse(json.dumps(ret), mimetype='application/json')
