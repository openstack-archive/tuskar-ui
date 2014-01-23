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


class ResourceCategoryInstanceTable(tables.DataTable):

    instance_name = tables.Column("name",
                                  verbose_name=_("Instance Name"))
    instance_status = tables.Column("status",
                                    verbose_name=_("Instance Status"))
    node_uuid = tables.Column(
        transform=lambda i: i.node.uuid,
        verbose_name=_("Node UUID"))
    node_cpu = tables.Column(
        transform=lambda i: i.node.properties['cpu'],
        verbose_name=_("Node CPU"))
    node_ram = tables.Column(
        transform=lambda i: i.node.properties['ram'],
        verbose_name=_("Node RAM (GB)"))
    node_local_disk = tables.Column(
        transform=lambda i: i.node.properties['local_disk'],
        verbose_name=_("Node Local Disk (TB)"))
    node_power_state = tables.Column(
        transform=lambda i: i.node.power_state,
        verbose_name=_("Power State"))

    class Meta:
        name = "resource_category__instancetable"
        verbose_name = _("Instances")
        table_actions = ()
        row_actions = ()


class LogTable(tables.DataTable):

    timestamp = tables.Column('event_time',
                              verbose_name=_("Timestamp"))
    resource_name = tables.Column('resource_name',
                                  verbose_name=_("Resource Name"))
    resource_status = tables.Column('resource_status',
                                    verbose_name=_("Status"))

    class Meta:
        name = "log"
        verbose_name = _("Log")
        multi_select = False
        table_actions = ()
        row_actions = ()
