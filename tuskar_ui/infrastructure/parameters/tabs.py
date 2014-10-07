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

from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from horizon import tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.parameters import tables


class ParametersTab(tabs.TableTab):
    table_classes = (tables.ParametersTable,)
    template_name = "horizon/common/_detail_table.html"

    def __init__(self, group, request, name, slug, parameters):
        self.name = name
        self.slug = slug
        self.parameters = parameters
        super(ParametersTab, self).__init__(group, request)

    def get_parameters_data(self):
        return self.parameters


class ParametersTabs(tabs.TabGroup):
    slug = "parameters"
    tabs = ()
    sticky = True
    template_name = "horizon/common/_items_count_tab_group.html"

    def __init__(self, request, **kwargs):
        super(ParametersTabs, self).__init__(request, **kwargs)
        plan = api.tuskar.Plan.get_the_plan(request)
        params = plan.parameter_list(include_key_parameters=False)
        tab_instances = []
        general_params = [p for p in params if p.role is None]
        if general_params:
            tab_instances.append((
                'global',
                ParametersTab(self, request,
                              _('Global'), 'global', general_params),
            ))
        for role in plan.role_list:
            role_params = [p for p in params
                           if p.role and p.role.uuid == role.uuid]
            if role_params:
                tab_instances.append((
                    role.name,
                    ParametersTab(self, request,
                                  role.name.title(), role.name, role_params),
                ))
        self._tabs = SortedDict(tab_instances)
