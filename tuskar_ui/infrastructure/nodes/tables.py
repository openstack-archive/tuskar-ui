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
        if not obj:
            # this is necessary because table actions use this function
            # with obj=None
            return True
        if api.node.NodeClient.ironic_enabled(request):
            return (getattr(obj, 'instance_uuid', None) is None and
                    obj.power_state not in api.node.POWER_ON_STATES)
        return getattr(obj, 'instance_uuid', None) is None

    def action(self, request, obj_id):
        api.node.Node.delete(request, obj_id)


class ActivateNode(tables.BatchAction):
    name = "activate"
    action_present = _("Activate")
    action_past = _("Activated")
    data_type_singular = _("Node")
    data_type_plural = _("Nodes")

    def allowed(self, request, obj=None):
        if not obj:
            # this is necessary because table actions use this function
            # with obj=None
            return True
        return (obj.cpus and obj.memory_mb and obj.local_gb and
                obj.cpu_arch)

    def action(self, request, obj_id):
        api.node.Node.set_maintenance(request, obj_id, False)
        api.node.Node.set_power_state(request, obj_id, 'off')


class SetPowerStateOn(tables.BatchAction):
    name = "set_power_state_on"
    action_present = _("Power On")
    action_past = _("Powering On")
    data_type_singular = _("Node")
    data_type_plural = _("Nodes")

    def allowed(self, request, obj=None):
        if not obj:
            # this is necessary because table actions use this function
            # with obj=None
            return True
        if api.node.NodeClient.ironic_enabled(request):
            return obj.power_state not in api.node.POWER_ON_STATES
        return False

    def action(self, request, obj_id):
        api.node.Node.set_power_state(request,
                                      obj_id,
                                      'on')


class SetPowerStateOff(tables.BatchAction):
    name = "set_power_state_off"
    action_present = _("Power Off")
    action_past = _("Powering Off")
    data_type_singular = _("Node")
    data_type_plural = _("Nodes")

    def allowed(self, request, obj=None):
        if not obj:
            # this is necessary because table actions use this function
            # with obj=None
            return True
        return (api.node.NodeClient.ironic_enabled(request)
                and obj.power_state in api.node.POWER_ON_STATES
                and getattr(obj, 'instance_uuid', None) is None)

    def action(self, request, obj_id):
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


def get_power_state_with_transition(node):
    if node.target_power_state and (
            node.power_state != node.target_power_state):
        return "{0} -> {1}".format(
            node.power_state, node.target_power_state)
    return node.power_state


def get_state_string(node):
    if node.state == api.node.DISCOVERING_STATE:
        return _('Discovering')
    if node.state == api.node.DISCOVERED_STATE:
        return _('Discovered')
    if node.state == api.node.PROVISIONED_STATE:
        return _('Provisioned')
    if node.state == api.node.PROVISIONING_FAILED_STATE:
        return _('Provisioning Failed')
    if node.state == api.node.PROVISIONING_STATE:
        return _('Provisioning')
    if node.state == api.node.FREE_STATE:
        return _('Free')
    return node.state


class BaseNodesTable(tables.DataTable):
    node = tables.Column('uuid',
                         link="horizon:infrastructure:nodes:detail",
                         verbose_name=_("Node Name"))
    role_name = tables.Column('role_name',
                              link=get_role_link,
                              verbose_name=_("Deployment Role"))
    cpus = tables.Column('cpus',
                         verbose_name=_("CPU (cores)"))
    memory_mb = tables.Column('memory_mb',
                              verbose_name=_("Memory (MB)"))
    local_gb = tables.Column('local_gb',
                             verbose_name=_("Disk (GB)"))
    power_status = tables.Column(get_power_state_with_transition,
                                 verbose_name=_("Power Status"))
    state = tables.Column(get_state_string,
                          verbose_name=_("Status"))

    class Meta:
        name = "nodes_table"
        verbose_name = _("Nodes")
        table_actions = (NodeFilterAction, SetPowerStateOn, SetPowerStateOff,
                         DeleteNode)
        row_actions = (SetPowerStateOn, SetPowerStateOff, DeleteNode)
        template = "horizon/common/_enhanced_data_table.html"

    def get_object_id(self, datum):
        return datum.uuid

    def get_object_display(self, datum):
        return datum.uuid


class AllNodesTable(BaseNodesTable):

    class Meta:
        name = "all_nodes_table"
        verbose_name = _("All")
        columns = ('node', 'cpus', 'memory_mb', 'local_gb', 'power_status',
                   'state')
        table_actions = (NodeFilterAction, SetPowerStateOn, SetPowerStateOff,
                         DeleteNode)
        row_actions = (SetPowerStateOn, SetPowerStateOff, DeleteNode)
        template = "horizon/common/_enhanced_data_table.html"


class ProvisionedNodesTable(BaseNodesTable):

    class Meta:
        name = "provisioned_nodes_table"
        verbose_name = _("Provisioned")
        table_actions = (NodeFilterAction, SetPowerStateOn, SetPowerStateOff,
                         DeleteNode)
        row_actions = (SetPowerStateOn, SetPowerStateOff, DeleteNode)
        template = "horizon/common/_enhanced_data_table.html"


class FreeNodesTable(BaseNodesTable):

    class Meta:
        name = "free_nodes_table"
        verbose_name = _("Free")
        columns = ('node', 'cpus', 'memory_mb', 'local_gb', 'power_status')
        table_actions = (NodeFilterAction, SetPowerStateOn, SetPowerStateOff,
                         DeleteNode)
        row_actions = (SetPowerStateOn, SetPowerStateOff, DeleteNode,)
        template = "horizon/common/_enhanced_data_table.html"


class MaintenanceNodesTable(BaseNodesTable):

    class Meta:
        name = "maintenance_nodes_table"
        verbose_name = _("Maintenance")
        columns = ('node', 'cpus', 'memory_mb', 'local_gb', 'power_status',
                   'state')
        table_actions = (NodeFilterAction, ActivateNode, SetPowerStateOn,
                         SetPowerStateOff, DeleteNode)
        row_actions = (ActivateNode, SetPowerStateOn, SetPowerStateOff,
                       DeleteNode)
        template = "horizon/common/_enhanced_data_table.html"
