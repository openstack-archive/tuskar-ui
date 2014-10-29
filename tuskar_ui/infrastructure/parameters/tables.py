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
from django.utils.html import escape  # noqa
from django.utils.safestring import mark_safe  # noqa
from django.utils.translation import ugettext_lazy as _
from horizon import tables


def name_with_tooltip(parameter):
    if not parameter.description:
        return parameter.stripped_name
    return mark_safe(
        u'%s&nbsp;<a class="help-icon fa fa-question-circle" '
        u'data-content="%s" tabindex="0" href="#" '
        u'title="%s"></a>' % (
            escape(parameter.stripped_name),
            escape(parameter.description),
            escape(parameter.stripped_name),
        ),
    )


def value_or_hidden(parameter):
    if parameter.hidden:
        return mark_safe(
            u'<span class="btn btn-xs btn-default password-button" '
            u'data-content="%s"'
            u'><i class="fa fa-eye"></i>&nbsp;%s</span>' % (
                escape(parameter.value),
                escape(_(u"Reveal")),
            ),
        )
    return parameter.value


class ParametersTable(tables.DataTable):
    name = tables.Column(
        name_with_tooltip,
        verbose_name=_("Parameter Name"),
        classes=['data-table-config-label'],
    )
    value = tables.Column(
        value_or_hidden,
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


class GlobalParametersTable(ParametersTable):
    class Meta(ParametersTable.Meta):
        name = "global_parameters"
        verbose_name = _("Global")


class ControllerParametersTable(ParametersTable):
    class Meta(ParametersTable.Meta):
        name = "controller_parameters"
        verbose_name = _("Controller")


class ComputeParametersTable(ParametersTable):
    class Meta(ParametersTable.Meta):
        name = "compute_parameters"
        verbose_name = _("Compute")


class BlockStorageParametersTable(ParametersTable):
    class Meta(ParametersTable.Meta):
        name = "block_storage_parameters"
        verbose_name = _("Block Storage")


class ObjectStorageParametersTable(ParametersTable):
    class Meta(ParametersTable.Meta):
        name = "object_storage_parameters"
        verbose_name = _("Object Storage")
