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

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs
from horizon import views as horizon_views

from openstack_dashboard.api import base as api_base

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms
from tuskar_ui.infrastructure.nodes import tabs
from tuskar_ui.utils import metering as metering_utils


class IndexView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.NodeTabs
    template_name = 'infrastructure/nodes/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['ironic_enabled'] = api.node.NodeClient.ironic_enabled(
            self.request)
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


class AutoDiscoverView(horizon_forms.ModalFormView):
    form_class = forms.AutoDiscoverNodeForm
    form_prefix = 'auto_discover_nodes'
    template_name = 'infrastructure/nodes/auto_discover.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:nodes:index')


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
                     metering_utils.url_part('hardware.cpu.load.1min', False),
                     None),
                    (_('CPU Utilization'),
                     metering_utils.url_part('hardware.system_stats.cpu.util',
                                             True),
                     '100'),
                    (_('Swap Utilization'),
                     metering_utils.url_part('hardware.memory.swap.util',
                                             True),
                     '100'),
                    (_('Disk I/O '),
                     metering_utils.url_part('disk-io', False),
                     None),
                    (_('Network I/O '),
                     metering_utils.url_part('network-io', False),
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
        barchart = bool(request.GET.get('barchart'))

        node_uuid = kwargs.get('node_uuid', None)
        if node_uuid:
            node = api.node.Node.get(request, node_uuid)
            try:
                instance_uuid = node.instance_uuid
            except AttributeError:
                json_output = None
            else:
                json_output = metering_utils.get_nodes_stats(
                    request, instance_uuid, meter, date_options=date_options,
                    date_from=date_from, date_to=date_to, stats_attr=stats_attr,
                    barchart=barchart)
        else:
            json_output = None

        return http.HttpResponse(json.dumps(json_output),
                                 mimetype='application/json')
