# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

import logging

from django import shortcuts
from django.core import urlresolvers
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import messages
from horizon import tables
from horizon import forms

from openstack_dashboard import api


LOG = logging.getLogger(__name__)


class CreateResourceClass(tables.LinkAction):
    name = "create_class"
    verbose_name = _("Create Class")
    url = "horizon:infrastructure:resource_management:resource_classes:create"
    classes = ("ajax-modal", "btn-create")


class UpdateResourceClass(tables.LinkAction):
    name = "edit_class"
    verbose_name = _("Edit Class")
    url = "horizon:infrastructure:resource_management:resource_classes:update"
    classes = ("ajax-modal", "btn-edit")


class DeleteResourceClass(tables.DeleteAction):
    data_type_singular = _("Resource Class")
    data_type_plural = _("Resource Classes")

    def delete(self, request, obj_id):
        try:
            api.management.ResourceClass.delete(request, obj_id)
        except:
            msg = _('Failed to delete resource class %s') % obj_id
            LOG.info(msg)
            redirect = urlresolvers.reverse(
                "horizon:infrastructure:resource_management:index")
            exceptions.handle(request, msg, redirect=redirect)


class ResourcesClassFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        pass


class ResourceClassesTable(tables.DataTable):
    name = tables.Column("name",
                         link=('horizon:infrastructure:'
                               'resource_management:resource_classes:detail'),
                         verbose_name=_("Class Name"))
    service_type = tables.Column("service_type",
                                 verbose_name=_("Class Type"))
    racks_count = tables.Column("racks_count",
                                verbose_name=_("Racks"),
                                empty_value="0")
    hosts_count = tables.Column("hosts_count",
                                verbose_name=_("Hosts"),
                                empty_value="0")

    class Meta:
        name = "resource_classes"
        verbose_name = ("Classes")
        table_actions = (ResourcesClassFilterAction, CreateResourceClass,
                         DeleteResourceClass)
        row_actions = (UpdateResourceClass, DeleteResourceClass)


class FlavorsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    vcpu = tables.Column(
        "vcpu",
        verbose_name=_('VCPU'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    ram = tables.Column(
        "ram",
        verbose_name=_('RAM (MB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    root_disk = tables.Column(
        "root_disk",
        verbose_name=_('Root Disk (GB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    ephemeral_disk = tables.Column(
        "ephemeral_disk",
        verbose_name=_('Ephemeral Disk (GB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    swap_disk = tables.Column(
        "swap_disk",
        verbose_name=_('Swap Disk (MB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    max_vms = tables.Column("max_vms",
                            auto='form_widget',
                            verbose_name=_("Max. VMs"),
                            form_widget=forms.NumberInput(),
                            form_widget_attributes={
                                'class': "test_class"})

    class Meta:
        name = "flavors"
        verbose_name = _("Flavors")
        multi_select = True
        multi_select_name = "flavors_object_ids"


class ResourcesFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        pass


class ResourcesTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    subnet = tables.Column("subnets",
                           verbose_name=_("Subnet"))
    region = tables.Column("region",
                           verbose_name=_("Region"))
    hosts_count = tables.Column("hosts_count",
                          verbose_name=_("Hosts"))
    total_cpu = tables.Column("total_cpu",
                              verbose_name=_("Total CPU"))
    total_ram = tables.Column("total_ram",
                              verbose_name=_("Total RAM"))
    total_disk = tables.Column("total_disk",
                               verbose_name=_("Total DISK"))

    class Meta:
        name = "resources"
        verbose_name = _("Resources")
        multi_select = True
        multi_select_name = "resources_object_ids"
        table_actions = (ResourcesFilterAction,)
