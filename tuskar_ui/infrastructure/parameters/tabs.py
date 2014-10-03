# Copyright 2012 Nebula, Inc.
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

from django.utils.translation import ugettext_lazy as _
from horizon import tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.parameters import tables


def get_parameter_tab_class(parameter_group, parameter_slug, parameters):

    class ParametersTab(tabs.TableTab):
        table_classes = (tables.ParametersTable,)
        name = parameter_group
        slug = parameter_slug
        template_name = "horizon/common/_detail_table.html"

        def __init__(self, tab_group, request):
            super(ParametersTab, self).__init__(tab_group, request)

        def get_parameters_data(self):
            return parameters

    return ParametersTab


class ParametersTabs(tabs.TabGroup):
    slug = "parameters"
    tabs = ()
    sticky = True
    template_name = "horizon/common/_items_count_tab_group.html"

    def __init__(self, request, **kwargs):
        plan = api.tuskar.Plan.get_the_plan(request)
        params = plan.parameter_list(include_key_parameters=False)

        general_params = [p for p in params if p.role is None]
        if general_params:
            self.tabs = self.tabs + (get_parameter_tab_class(_('Global'),
                                                             'global',
                                                             general_params),)
        for role in plan.role_list:
            role_params = [p for p in params if (p.role
                                                 and p.role.uuid == role.uuid)]
            if role_params:
                self.tabs = self.tabs + (
                    get_parameter_tab_class(role.name.capitalize(),
                                            role.name,
                                            role_params),)

        super(ParametersTabs, self).__init__(request, **kwargs)
