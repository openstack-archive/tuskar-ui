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

import logging

from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard import api


LOG = logging.getLogger(__name__)


class DeleteRacks(tables.DeleteAction):
    data_type_singular = _("Rack")
    data_type_plural = _("Racks")

    def delete(self, request, obj_id):
        api.management.Rack.delete(request, obj_id)


class CreateRack(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Rack")
    url = "horizon:infrastructure:resource_management:racks:create"
    classes = ("ajax-modal", "btn-create")


class EditRack(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Rack")
    url = "horizon:infrastructure:resource_management:racks:edit"
    classes = ("ajax-modal", "btn-edit")


class RacksFilterAction(tables.FilterAction):

    def filter(self, table, racks, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        return [rack for rack in racks
                if q in rack.name.lower()]


class RacksTable(tables.DataTable):
    name = tables.Column('name',
                         link=("horizon:infrastructure:resource_management"
                               ":racks:detail"),
                         verbose_name=_("Rack Name"))
    location = tables.Column('location', verbose_name=_("Location"))
    subnet = tables.Column('subnet', verbose_name=_("IP Subnet"))
    host_count = tables.Column('hosts_count', verbose_name=_("Hosts"))

    class Meta:
        name = "racks"
        verbose_name = _("Racks")
        table_actions = (CreateRack, DeleteRacks, RacksFilterAction)
        row_actions = (EditRack, DeleteRacks)
