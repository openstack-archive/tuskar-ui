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
import django.forms
import django.http
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base
from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs
from horizon.utils import memoized

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms
from tuskar_ui.infrastructure.nodes import tables
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
    form_class = forms.RegisterNodeFormset
    form_prefix = 'register_nodes'
    template_name = 'infrastructure/nodes/register.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:nodes:index')

    def get_data(self):
        return []

    def get_form(self, form_class):
        initial = []
        if self.request.META.get('CONTENT_TYPE', '').startswith(
                'multipart/form-data'):
            csv_form = forms.UploadNodeForm(self.request,
                                            files=self.request.FILES)
            if csv_form.is_valid():
                initial = csv_form.get_data()
            return forms.RegisterNodeFormset(
                None,
                initial=initial,
                prefix=self.form_prefix,
            )
        return forms.RegisterNodeFormset(
            self.request.POST or None,
            initial=initial,
            prefix=self.form_prefix,
        )


class UploadView(horizon_forms.ModalFormView):
    form_class = forms.UploadNodeForm
    template_name = 'infrastructure/nodes/upload.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:nodes:index')

    def post(self, request, *args, **kwargs):
        # This form's POST is handled in RegisterView.
        raise exceptions.NotFound()


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.NodeDetailTabs
    template_name = 'infrastructure/nodes/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        node = self.get_data()

        if node.maintenance:
            table = tables.MaintenanceNodesTable(self.request)
        else:
            table = tables.RegisteredNodesTable(self.request)

        context['node'] = node
        context['title'] = _("Node: %(uuid)s") % {'uuid': node.uuid}
        context['url'] = self.get_redirect_url()
        context['actions'] = table.render_row_actions(node)
        return context

    @memoized.memoized_method
    def get_data(self):
        node_uuid = self.kwargs.get('node_uuid')
        node = api.node.Node.get(self.request, node_uuid,
                                 _error_redirect=self.get_redirect_url())
        return node

    def get_tabs(self, request, **kwargs):
        node = self.get_data()
        return self.tab_group_class(self.request, node=node, **kwargs)

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:infrastructure:nodes:index')


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
            # Aggregated stats for all nodes
            instance_uuid = None

        json_output = metering_utils.get_nodes_stats(
            request, instance_uuid, meter, date_options=date_options,
            date_from=date_from, date_to=date_to,
            stats_attr=stats_attr, barchart=barchart)

        return django.http.HttpResponse(
            json.dumps(json_output), content_type='application/json')
