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

from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import tables


class NodesTable(tables.DataTable):
    service_host = tables.Column(
        "service_host",
        verbose_name=_("Service Host"),
        link=("horizon:infrastructure:resources.management:detail"))
    mac_address = tables.Column("mac_address", verbose_name=_("MAC Address"))
    pm_address = tables.Column("pm_address",
                               verbose_name=_("Management Address"))
    status = tables.Column("status", verbose_name=_("Status"))
    usage = tables.Column("usage", verbose_name=_("Usage"))

    class Meta:
        name = "nodes_table"
        verbose_name = _("Nodes")
        table_actions = ()
        row_actions = ()

    def get_object_display(self, datum):
        return datum.service_host
