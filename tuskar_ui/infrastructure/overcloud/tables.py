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

from tuskar_ui.infrastructure.nodes import tables as nodes_tables


class OvercloudRoleNodeTable(nodes_tables.DeployedNodesTable):

    class Meta:
        name = "overcloud_role__nodetable"
        verbose_name = _("Nodes")
        table_actions = ()
        row_actions = ()


class ConfigurationTable(tables.DataTable):

    key = tables.Column(lambda parameter: parameter[0],
                        verbose_name=_("Attribute Name"))
    value = tables.Column(lambda parameter: parameter[1],
                          verbose_name=_("Attribute Value"))

    class Meta:
        name = "configuration"
        verbose_name = _("Configuration")
        multi_select = False
        table_actions = ()
        row_actions = ()

    def get_object_id(self, datum):
        return datum[0]


class LogTable(tables.DataTable):

    timestamp = tables.Column('event_time',
                              verbose_name=_("Timestamp"),
                              attrs={'data-type': 'timestamp'})
    resource_name = tables.Column('resource_name',
                                  verbose_name=_("Resource Name"))
    resource_status = tables.Column('resource_status',
                                    verbose_name=_("Status"))
    resource_status_reason = tables.Column('resource_status_reason',
                                           verbose_name=_("Reason"))

    class Meta:
        name = "log"
        verbose_name = _("Log")
        multi_select = False
        table_actions = ()
        row_actions = ()
