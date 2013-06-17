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

from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard import api


class DeleteHosts(tables.DeleteAction):
    data_type_singular = _("Host")
    data_type_plural = _("Hosts")

    def delete(self, request, obj_id):
        api.management.host_delete(request, obj_id)


class HostsFilterAction(tables.FilterAction):
    def filter(self, table, hosts, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        return [host for host in hosts if q in host.name.lower()]


class HostsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("error", False),
    )
    name = tables.Column("name",
                         link=("horizon:infrastructure:"
                               "resource_management:hosts:detail"),
                         verbose_name=_("Name"))
    mac_address = tables.Column("mac_address", verbose_name=_("MAC Address"))
    ip_address = tables.Column("ip_address", verbose_name=_("IP Address"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)
    usage = tables.Column("usage",
                          verbose_name=_("Usage"))

    class Meta:
        name = "hosts"
        verbose_name = _("Hosts")
        table_actions = (DeleteHosts, HostsFilterAction)
        row_actions = (DeleteHosts,)


class UnrackedHostsTable(HostsTable):

    class Meta:
        name = "unracked_hosts"
        verbose_name = _("Unracked Hosts")
        table_actions = ()
        row_actions = ()
