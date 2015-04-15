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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import horizon.forms
import horizon.tables

from tuskar_ui import api
from tuskar_ui.infrastructure.parameters import forms


class SimpleServiceConfigView(horizon.forms.ModalFormView):
    form_class = forms.SimpleEditServiceConfig
    success_url = reverse_lazy('horizon:infrastructure:parameters:index')
    submit_label = _("Save Configuration")
    template_name = "infrastructure/parameters/simple_service_config.html"

    def get_initial(self):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        compute_prefix = plan.get_role_by_name('Compute').parameter_prefix
        controller_prefix = plan.get_role_by_name(
            'Controller').parameter_prefix

        cinder_iscsi_helper = plan.parameter_value(
            controller_prefix + 'CinderISCSIHelper')
        cloud_name = plan.parameter_value(
            controller_prefix + 'CloudName')
        extra_config = plan.parameter_value(
            controller_prefix + 'ExtraConfig')
        neutron_public_interface = plan.parameter_value(
            controller_prefix + 'NeutronPublicInterface')
        ntp_server = plan.parameter_value(
            controller_prefix + 'NtpServer')
        snmp_password = plan.parameter_value(
            controller_prefix + 'SnmpdReadonlyUserPassword')
        virt_type = plan.parameter_value(
            compute_prefix + 'NovaComputeLibvirtType')
        return {
            'cinder_iscsi_helper': cinder_iscsi_helper,
            'cloud_name': cloud_name,
            'neutron_public_interface': neutron_public_interface,
            'ntp_server': ntp_server,
            'extra_config': extra_config,
            'neutron_public_interface': neutron_public_interface,
            'snmp_password': snmp_password,
            'virt_type': virt_type}


class IndexView(horizon.forms.ModalFormView):
    form_class = forms.ServiceConfig
    form_id = "service_config"
    template_name = "infrastructure/parameters/index.html"

    def get_initial(self):
        self.plan = api.tuskar.Plan.get_the_plan(self.request)
        self.parameters = self.plan.parameter_list(
            include_key_parameters=False)
        return {p.name: p.value for p in self.parameters}

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        advanced_edit_action = {
            'name': _('Advanced Configuration'),
            'url': reverse('horizon:infrastructure:parameters:'
                           'advanced_service_configuration'),
            'icon': 'fa-pencil',
            'ajax_modal': False,
        }
        simplified_edit_action = {
            'name': _('Simplified Configuration'),
            'url': reverse('horizon:infrastructure:parameters:'
                           'simple_service_configuration'),
            'icon': 'fa-pencil-square-o',
            'ajax_modal': True,
        }
        context['header_actions'] = [advanced_edit_action,
                                     simplified_edit_action]
        return context


class AdvancedServiceConfigView(IndexView):
    form_class = forms.AdvancedEditServiceConfig
    form_id = "advanced_service_config"
    success_url = reverse_lazy('horizon:infrastructure:parameters:index')
    submit_label = _("Save Configuration")
    submit_url = reverse_lazy('horizon:infrastructure:parameters:'
                              'advanced_service_configuration')
    template_name = "infrastructure/parameters/advanced_service_config.html"

    def get_context_data(self, **kwargs):
        context = super(AdvancedServiceConfigView,
                        self) .get_context_data(**kwargs)
        context['header_actions'] = []
        return context
