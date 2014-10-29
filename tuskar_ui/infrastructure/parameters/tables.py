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
from django.utils.html import escape # noqa
from django.utils.safestring import mark_safe # noqa
from django.utils.translation import ugettext_lazy as _
from horizon import tables

def name_with_tooltip(parameter):
    return mark_safe(u'<span title="{}" '
                     u'data-toggle="tooltip" '
                     u'data-placement="right" '
                     u'>{}</span>'.format(
        escape(parameter.stripped_name),
        escape(parameter.description),
    ))

class ParametersTable(tables.DataTable):
    name = tables.Column(
        name_with_tooltip,
        verbose_name=_("Parameter Name"),
        classes=['data-table-config-label'],
    )
    value = tables.Column(
        'value',
        verbose_name=_("Value"),
        classes=['data-table-config-value'],
    )

    def get_object_id(self, datum):
        return datum.name

    class Meta:
        name = "parameters"
        verbose_name = _("Service Configuration")
        table_actions = ()
        row_actions = ()
        template = "horizon/common/_definition_list_data_table.html"
