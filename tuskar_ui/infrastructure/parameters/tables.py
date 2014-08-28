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

from horizon import tables


class ParametersTable(tables.DataTable):
    label = tables.Column('label',
                          verbose_name=_("Parameter Name"))
    value = tables.Column('value',
                          verbose_name=_("Default Value"))
    description = tables.Column('description',
                                verbose_name=("Detailed Description"))

    class Meta:
        name = "parameters"
        verbose_name = _("Service Configuration")
        table_actions = ()
        row_actions = ()
