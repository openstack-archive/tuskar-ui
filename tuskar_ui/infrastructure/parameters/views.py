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
import horizon.forms
from horizon import tables as horizon_tables

from tuskar_ui import api
from tuskar_ui.infrastructure.parameters import forms
from tuskar_ui.infrastructure.parameters import tables


class ServiceConfigView(horizon.forms.ModalFormView):
    template_name = "infrastructure/parameters/service_config.html"
    form_class = forms.EditServiceConfig
    success_url = reverse_lazy('horizon:infrastructure:parameters:index')

    def get_initial(self):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        compute_prefix = plan.get_role_by_name('compute').parameter_prefix

        virt_type = plan.parameter_value(
            compute_prefix + 'NovaComputeLibvirtType')
        #TODO(tzumainn): what if compute and control values are different...
        snmp_password = plan.parameter_value(
            compute_prefix + 'SnmpdReadonlyUserPassword')

        return {'virt_type': virt_type,
                'snmp_password': snmp_password}


class IndexView(horizon_tables.DataTableView):
    table_class = tables.ParametersTable
    template_name = "infrastructure/parameters/index.html"

    def get_data(self):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        return plan.parameter_list(include_key_parameters=False)
