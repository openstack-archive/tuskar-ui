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

from django.utils.translation import ugettext_lazy as _

import horizon.tables
from horizon.tables import formset

from tuskar_ui.infrastructure.plans import forms


class ConfigurationTable(horizon.tables.DataTable):

    key = horizon.tables.Column(lambda parameter: parameter[0],
                        verbose_name=_("Attribute Name"))
    value = horizon.tables.Column(lambda parameter: parameter[1],
                          verbose_name=_("Attribute Value"))

    class Meta:
        name = "configuration"
        verbose_name = _("Configuration")
        multi_select = False
        table_actions = ()
        row_actions = ()

    def get_object_id(self, datum):
        return datum[0]


class PlanRolesTable(formset.FormsetDataTable):
    formset_class = forms.PlanRoleFormset

    class Meta:
        name = "setup_roles"
        verbose_name = _("Setup Roles")
        table_actions = ()
        row_actions = ()
