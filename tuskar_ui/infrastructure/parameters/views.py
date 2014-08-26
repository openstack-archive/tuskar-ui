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

import horizon.forms
from horizon import tables as horizon_tables

from tuskar_ui import api
from tuskar_ui.infrastructure.parameters import forms
from tuskar_ui.infrastructure.parameters import tables


class ServiceParameter:
    def __init__(self, params_dict, id):
        self.id = id
        self.label = params_dict.get('name')
        self.value = params_dict.get('default')
        self.category = params_dict.get('parameter_group')
        self.description = params_dict.get('description')


class ServiceConfigView(horizon.forms.ModalFormView):
    template_name = "infrastructure/parameters/service_config.html"
    form_class = forms.EditServiceConfig

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        context = super(ServiceConfigView, self).get_context_data(
            *args, **kwargs)
        context.update(self.get_data(self.request, context))
        return context

    def get_data(self, request, context, *args, **kwargs):
        plan = api.tuskar.Plan.get_the_plan(self.request)

        context['plan'] = plan
        base_parameters = plan.parameter_list(
            include_key_parameters=False)
        context['parameters'] = [ServiceParameter(param, ind)
                                 for ind, param in enumerate(base_parameters)]
        return context


class IndexView(horizon_tables.DataTableView):
    table_class = tables.ParametersTable
    template_name = "infrastructure/parameters/index.html"

    def get_data(self):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        base_parameters = plan.parameter_list(
            include_key_parameters=False)
        params = [ServiceParameter(param, ind)
                  for ind, param in enumerate(base_parameters)]
        return params
