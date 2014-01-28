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


class ResourceCategoryNodeTable(tables.DataTable):

    ipmi_address = tables.Column(lambda node: node.driver_info['ipmi_address'],
                                 verbose_name=_("Node"))
    cpu = tables.Column(lambda node: node.properties['cpu'],
                        verbose_name=_("CPU (cores)"))
    ram = tables.Column(lambda node: node.properties['ram'],
                        verbose_name=_("Memory (GB)"))
    local_disk = tables.Column(lambda node: node.properties['local_disk'],
                               verbose_name=_("Local Disk (TB)"))
    instance_status = tables.Column(lambda node: node.instance.status,
                                    verbose_name=_("Instance Status"))
    power_state = tables.Column("power_state",
                                verbose_name=_("Power"),
                                status=True,
                                status_choices=(
                                    ('on', True),
                                    ('off', False),
                                    ('rebooting', None)
                                ))

    def get_object_id(self, datum):
        return datum.uuid

    class Meta:
        name = "resource_category__nodetable"
        verbose_name = _("Nodes")
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
