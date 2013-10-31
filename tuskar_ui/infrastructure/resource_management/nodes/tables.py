# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tables

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management.nodes import forms \
    as nodes_forms
import tuskar_ui.tables


class DeleteNodes(tables.DeleteAction):
    data_type_singular = _("Node")
    data_type_plural = _("Nodes")

    def delete(self, request, obj_id):
        try:
            tuskar_node = tuskar.TuskarNode.get(request, obj_id)
            tuskar_node.remove_from_rack(request)
        except Exception:
            exceptions.handle(request, _("Error deleting node."))
            return False


class NodesFilterAction(tables.FilterAction):
    def filter(self, table, nodes, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        # This is used both for Tuskar and Baremetal nodes.
        return [node for node in nodes if q in node.name.lower()]


class NodesTable(tables.DataTable):
    service_host = tables.Column(
        "service_host",
        verbose_name=_("Service Host"),
        link=("horizon:infrastructure:resource_management:nodes:detail"))
    mac_address = tables.Column("mac_address", verbose_name=_("MAC Address"))
    pm_address = tables.Column("pm_address",
                               verbose_name=_("Management Address"))
    status = tables.Column("status", verbose_name=_("Status"))
    usage = tables.Column("usage", verbose_name=_("Usage"))

    class Meta:
        name = "nodes_table"
        verbose_name = _("Nodes")
        table_actions = (DeleteNodes, NodesFilterAction)
        row_actions = (DeleteNodes,)

    def get_object_display(self, datum):
        return datum.service_host


class UnrackedNodesTable(NodesTable):

    class Meta:
        name = "unracked_nodes"
        verbose_name = _("Unracked Nodes")
        table_actions = ()
        row_actions = ()


class NodesFormsetTable(tuskar_ui.tables.FormsetDataTable):
    service_host = tables.Column('service_host',
                                 verbose_name=_("Service Host"))
    mac_address = tables.Column('mac_address', verbose_name=_("MAC Address"))

    cpus = tables.Column('cpus', verbose_name=_("CPUs"))
    memory_mb = tables.Column('memory_mb', verbose_name=_("Memory (MB)"))
    local_gb = tables.Column('local_gb', verbose_name=_("Local Disk (GB)"))

    pm_address = tables.Column('pm_address',
                               verbose_name=_("Power Management IP"))
    pm_user = tables.Column('pm_user', verbose_name=_("Power Management User"))
    pm_password = tables.Column('pm_password',
                                verbose_name=_("Power Management Password"))

    terminal_port = tables.Column('terminal_port',
                                  verbose_name=_("Terminal Port"))

    # This is needed for the formset with can_delete=True
    DELETE = tables.Column('DELETE', verbose_name=_("Delete"))

    formset_class = nodes_forms.NodeFormset

    class Meta:
        name = "nodes"
        verbose_name = _("Nodes")
        table_actions = ()
        multi_select = False
