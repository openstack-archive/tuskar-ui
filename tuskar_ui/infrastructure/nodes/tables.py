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

from django.template import defaultfilters
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from tuskar_ui import api


class DeleteNode(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Deleting")
    data_type_singular = _("Node")
    data_type_plural = _("Nodes")
    classes = ('btn-danger',)

    def allowed(self, request, obj=None):
        return getattr(obj, 'instance', None) is None

    def action(self, request, obj_id):
        api.Node.delete(request, obj_id)


class NodeFilterAction(tables.FilterAction):
    def filter(self, table, nodes, filter_string):
        """Really naive case-insensitive search."""
        q = filter_string.lower()

        def comp(node):
            return any(q in attr for attr in
                       (node.ip_address,
                        node.properties['cpu'],
                        node.properties['ram'],
                        node.properties['local_disk'],))

        return filter(comp, nodes)


class NodesTable(tables.DataTable):
    node = tables.Column(lambda node: node.driver_info['ip_address'],
                         link="horizon:infrastructure:nodes:detail",
                         verbose_name=_("Node"))

    # TODO(lsmola) waits for Ironic
    # architecture = tables.Column(
    #     lambda node: "",
    #     verbose_name=_("Architecture"))

    cpu = tables.Column(lambda node: node.properties['cpu'],
                        verbose_name=_("CPU (cores)"))
    ram = tables.Column(lambda node: defaultfilters.filesizeformat(
                        node.properties['ram']),
                        verbose_name=_("RAM"))
    local_disk = tables.Column(lambda node: defaultfilters.filesizeformat(
                               node.properties['local_disk']),
                               verbose_name=_("Local Disk"))
    power_state = tables.Column("power_state",
                                verbose_name=_("Power"),
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
        return datum.id

    def get_object_display(self, datum):
        return datum.uuid


class FreeNodesTable(NodesTable):

    # TODO(jtomasek): waits for Ironic to expose IP
    # node = tables.Column(lambda node: node.driver_info['ipmi_address'],
    #                      link="horizon:infrastructure:nodes:detail",
    #                      verbose_name=_("Node"))
    node = tables.Column("uuid",
                         link="horizon:infrastructure:nodes:detail",
                         verbose_name=_("Node"))

    class Meta:
        name = "free_nodes"
        verbose_name = _("Free Nodes")
        table_actions = (DeleteNode,
                         NodeFilterAction,)
        row_actions = (DeleteNode,)


class DeployedNodesTable(NodesTable):

    deployment_role = tables.Column(
        lambda node: node.overcloud_role.name,
        verbose_name=_("Deployment Role"))

    # TODO(lsmola) waits for Ceilometer baremetal metrics
    # capacity = tables.Column(
    #     lambda node: "",
    #     verbose_name=_("Capacity"))

    health = tables.Column('instance_status',
                           verbose_name=_("Health"))

    class Meta:
        name = "deployed_nodes"
        verbose_name = _("Deployed Nodes")
        table_actions = (NodeFilterAction,)
        row_actions = ()
        columns = ('node', 'deployment_role', 'capacity', 'architecture',
                   'cpu', 'ram', 'local_disk', 'health', 'power_state')
