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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import horizon.forms
from horizon import tabs as horizon_tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.parameters import forms
from tuskar_ui.infrastructure.parameters import tabs


class ServiceConfigView(horizon.forms.ModalFormView):
    form_class = forms.EditServiceConfig
    success_url = reverse_lazy('horizon:infrastructure:parameters:index')
    submit_label = _("Save Configuration")
    template_name = "infrastructure/parameters/service_config.html"

    def get_initial(self):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        compute_prefix = plan.get_role_by_name('compute').parameter_prefix
        controller_prefix = plan.get_role_by_name(
            'controller').parameter_prefix

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



class IndexView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.ParametersTabs
    template_name = "infrastructure/parameters/index.html"
