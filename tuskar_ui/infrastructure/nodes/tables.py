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

from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from horizon import tables


class NodesTable(tables.DataTable):

    uuid = tables.Column("uuid",
                         verbose_name=_("UUID"))
    mac_addresses = tables.Column("addresses",
                                  verbose_name=_("MAC Addresses"),
                                  wrap_list=True,
                                  filters=(filters.unordered_list,))
    ipmi_address = tables.Column(lambda node: node.driver_info['ipmi_address'],
                                 verbose_name=_("IPMI Address"))
    cpu = tables.Column(lambda node: node.properties['cpu'],
                        verbose_name=_("CPU"))
    ram = tables.Column(lambda node: node.properties['ram'],
                        verbose_name=_("RAM (GB)"))
    local_disk = tables.Column(lambda node: node.properties['local_disk'],
                               verbose_name=_("Local Disk (TB)"))
    status = tables.Column("power_state",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=(
                               ('on', True),
                               ('off', False),
                               ('rebooting', None)
                           ))

    class Meta:
        name = "nodes_table"
        verbose_name = _("Nodes")
        table_actions = ()
        row_actions = ()

    def get_object_id(self, datum):
        return datum.uuid

    def get_object_display(self, datum):
        return datum.uuid


class FreeNodesTable(NodesTable):

    class Meta:
        name = "free_nodes"
        verbose_name = _("Free Nodes")
        table_actions = ()
        row_actions = ()


class ResourceNodesTable(NodesTable):

    class Meta:
        name = "resource_nodes"
        verbose_name = _("Resource Nodes")
        table_actions = ()
        row_actions = ()
