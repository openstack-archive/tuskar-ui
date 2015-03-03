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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
import django.forms
import django.http
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base
from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs
from horizon.utils import memoized
from openstack_dashboard.api import glance

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms
from tuskar_ui.infrastructure.nodes import tabs
import tuskar_ui.infrastructure.views as infrastructure_views
from tuskar_ui.utils import metering as metering_utils
from tuskar_ui.utils import utils


def get_kernel_images(request):
    try:
        kernel_images = glance.image_list_detailed(
            request,
            )[0]
        kernel_images = [image for image in kernel_images
                         if utils.check_image_type(image, 'deploy kernel')]
    except Exception:
        exceptions.handle(request,
                          _('Unable to retrieve kernel image list.'))
        kernel_images = []
    return kernel_images


def get_ramdisk_images(request):
    try:
        ramdisk_images = glance.image_list_detailed(
            request,
            )[0]
        ramdisk_images = [image for image in ramdisk_images
                          if utils.check_image_type(
                              image, 'deploy ramdisk')]
    except Exception:
        exceptions.handle(request,
                          _('Unable to retrieve ramdisk image list.'))
        ramdisk_images = []
    return ramdisk_images


class IndexView(infrastructure_views.ItemCountMixin,
                horizon_tabs.TabbedTableView):
    tab_group_class = tabs.NodeTabs
    template_name = 'infrastructure/nodes/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        register_action = {
            'name': _('Register Nodes'),
            'url': reverse('horizon:infrastructure:nodes:register'),
            'icon': 'fa-plus',
            'ajax_modal': True,
        }
        context['header_actions'] = [register_action]
        return context

    @memoized.memoized_method
    def get_data(self):
        return api.node.Node.list(self.request)

    def get_tabs(self, request, **kwargs):
        nodes = self.get_data()
        return self.tab_group_class(request, nodes=nodes, **kwargs)


class RegisterView(horizon_forms.ModalFormView):
    form_class = forms.RegisterNodeFormset
    form_prefix = 'register_nodes'
    template_name = 'infrastructure/nodes/register.html'
    success_url = reverse_lazy('horizon:infrastructure:nodes:index')
    submit_label = _("Register Nodes")

    def get_data(self):
        return []

    def get_form(self, form_class):
        initial = []

        if self.request.FILES:
            csv_form = forms.UploadNodeForm(self.request,
                                            data=self.request.POST,
                                            files=self.request.FILES)
            if csv_form.is_valid():
                initial = csv_form.get_data()
            formset = forms.RegisterNodeFormset(
                self.request.POST,
                prefix=self.form_prefix,
                request=self.request,
                kernel_images=get_kernel_images(self.request),
                ramdisk_images=get_ramdisk_images(self.request)
            )
            if formset.is_valid():
                initial += formset.cleaned_data
            formset = forms.RegisterNodeFormset(
                None,
                initial=initial,
                prefix=self.form_prefix,
                request=self.request,
                kernel_images=get_kernel_images(self.request),
                ramdisk_images=get_ramdisk_images(self.request)
            )
            formset.extra = 0
            return formset
        return forms.RegisterNodeFormset(
            self.request.POST or None,
            initial=initial,
            prefix=self.form_prefix,
            request=self.request,
            kernel_images=get_kernel_images(self.request),
            ramdisk_images=get_ramdisk_images(self.request)
        )

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context['upload_form'] = forms.UploadNodeForm(self.request)
        return context


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.NodeDetailTabs
    template_name = 'infrastructure/nodes/detail.html'

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
            instance_uuid = node.instance_uuid
        else:
            # Aggregated stats for all nodes
            instance_uuid = None

        json_output = metering_utils.get_nodes_stats(
            request, node_uuid, instance_uuid, meter,
            date_options=date_options, date_from=date_from, date_to=date_to,
            stats_attr=stats_attr, barchart=barchart)

        return django.http.HttpResponse(
            json.dumps(json_output), content_type='application/json')
