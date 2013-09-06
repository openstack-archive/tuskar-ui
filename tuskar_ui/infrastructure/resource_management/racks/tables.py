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

from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import tables

from tuskar_ui import api as tuskar

LOG = logging.getLogger(__name__)


class DeleteRacks(tables.DeleteAction):
    data_type_singular = _("Rack")
    data_type_plural = _("Racks")

    def delete(self, request, obj_id):
        tuskar.Rack.delete(request, obj_id)


class CreateRack(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Rack")
    url = "horizon:infrastructure:resource_management:racks:create"
    classes = ("ajax-modal", "btn-create")


class UploadRack(tables.LinkAction):
    name = "upload"
    verbose_name = _("Upload Rack")
    url = "horizon:infrastructure:resource_management:racks:upload"
    classes = ("ajax-modal", "btn-upload")


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


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, rack_id):
        rack = tuskar.Rack.get(request, rack_id)
        return rack


class RacksTable(tables.DataTable):
    STATUS_CHOICES = (
        ("unprovisioned", False),
        ("provisioning", None),
        ("active", True),
        ("error", False),
    )
    name = tables.Column('name',
                         link=("horizon:infrastructure:resource_management"
                               ":racks:detail"),
                         verbose_name=_("Rack Name"))
    subnet = tables.Column('subnet', verbose_name=_("IP Subnet"))
    resource_class = tables.Column('get_resource_class',
                                    verbose_name=_("Class"),
                                    filters=(lambda resource_class:
                                                 (resource_class and
                                                  resource_class.name)
                                             or None,))
    node_count = tables.Column('nodes_count', verbose_name=_("Nodes"))
    state = tables.Column('state',
                          verbose_name=_("State"),
                          status=True,
                          status_choices=STATUS_CHOICES)
    usage = tables.Column(
        'vm_capacity',
        verbose_name=_("Usage"),
        filters=(lambda vm_capacity:
                     (vm_capacity.value and
                      "%s %%" % int(round((100 / float(vm_capacity.value)) *
                                          vm_capacity.usage, 0))) or None,))

    class Meta:
        name = "racks"
        row_class = UpdateRow
        status_columns = ["state"]
        verbose_name = _("Racks")
        table_actions = (UploadRack, CreateRack, DeleteRacks,
                         RacksFilterAction)
        row_actions = (EditRack, DeleteRacks)


class UploadRacksTable(tables.DataTable):
    name = tables.Column("name")
    subnet = tables.Column("subnet")
    nodes_count = tables.Column("nodes_count")
    #region = tables.Column("region")

    class Meta:
        name = "uploaded_racks"
        verbose_name = " "
