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

import time

from django.core.urlresolvers import reverse
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
        return getattr(obj, 'instance_uuid', None) is None

    def action(self, request, obj_id):
        api.node.Node.delete(request, obj_id)


class ActivateNode(tables.BatchAction):
    name = "activate"
    action_present = _("Activate")
    action_past = _("Activated")
    data_type_singular = _("Node")
    data_type_plural = _("Nodes")

    def action(self, request, obj_id):
        api.node.Node.set_maintenance(request, obj_id, False)
        time.sleep(60)
        api.node.Node.set_power_state(request,
                                      obj_id,
                                      'off')


class NodeFilterAction(tables.FilterAction):
    def filter(self, table, nodes, filter_string):
        """Really naive case-insensitive search."""
        q = filter_string.lower()

        def comp(node):
            return any(q in attr for attr in
                       (node.ip_address,
                        node.cpus,
                        node.memory_mb,
                        node.local_gb,))

        return filter(comp, nodes)


def get_role_link(datum):
    # TODO(tzumainn): this could probably be done more efficiently
    # by getting the resource for all nodes at once
    if datum.role_id:
        return reverse('horizon:infrastructure:roles:detail',
                       kwargs={'role_id': datum.role_id})


class RegisteredNodesTable(tables.DataTable):
    node = tables.Column('uuid',
                         link="horizon:infrastructure:nodes:detail",
                         verbose_name=_("Node Name"))
    instance_ip = tables.Column(lambda n:
                                n.ip_address if n.instance else '-',
                                verbose_name=_("Instance IP"))
    provisioning_status = tables.Column('provisioning_status',
                                        verbose_name=_("Provisioned"))
    role_name = tables.Column('role_name',
                              link=get_role_link,
                              verbose_name=_("Deployment Role"))
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
        verbose_name = _("Registered Nodes")
        table_actions = (NodeFilterAction,)
        row_actions = (DeleteNode,)

    def get_object_id(self, datum):
        return datum.uuid

    def get_object_display(self, datum):
        return datum.uuid


class MaintenanceNodesTable(tables.DataTable):
    node = tables.Column('uuid',
                         link="horizon:infrastructure:nodes:detail",
                         verbose_name=_("Node Name"))
    cpu_arch = tables.Column('cpu_arch',
                             verbose_name=_("Arch."))
    cpus = tables.Column('cpus',
                         verbose_name=_("CPU (cores)"))
    memory_mb = tables.Column('memory_mb',
                              verbose_name=_("Memory (MB)"))
    local_gb = tables.Column('local_gb',
                             verbose_name=_("Disk (GB)"))
    driver = tables.Column('driver',
                           verbose_name=_("Driver"))
    nics = tables.Column(lambda n: len(n.addresses),
                         verbose_name=_("NICs"))

    class Meta:
        name = "maintenance_nodes_table"
        verbose_name = _("Nodes (Maintenance)")
        table_actions = (NodeFilterAction,)
        row_actions = (ActivateNode, DeleteNode,)

    def get_object_id(self, datum):
        return datum.uuid

    def get_object_display(self, datum):
        return datum.uuid
