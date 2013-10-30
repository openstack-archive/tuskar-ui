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
import re

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tables

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management.flavors\
    import forms as flavors_forms
from tuskar_ui.infrastructure.resource_management.racks\
    import tables as racks_tables
from tuskar_ui.infrastructure.resource_management import resource_classes
from tuskar_ui.infrastructure.resource_management.resource_classes\
    import forms
import tuskar_ui.tables


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
            tuskar.ResourceClass.delete(request, obj_id)
        except Exception:
            msg = _('Failed to delete resource class %s') % obj_id
            LOG.info(msg)
            redirect = urlresolvers.reverse(
                "horizon:infrastructure:resource_management:index")
            exceptions.handle(request, msg, redirect=redirect)


class ResourcesClassFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        pass


class ResourceClassesTable(tables.DataTable):
    name = tables.Column(
        "name", link=("horizon:infrastructure:"
                      "resource_management:resource_classes:detail"),
        verbose_name=_("Class Name"))
    service_type = tables.Column("service_type", verbose_name=_("Class Type"))
    racks_count = tables.Column("racks_count", verbose_name=_("Racks"),
                                empty_value="0")
    nodes_count = tables.Column("nodes_count", verbose_name=_("Nodes"),
                                empty_value="0")

    class Meta:
        name = "resource_classes"
        verbose_name = ("Classes")
        table_actions = (ResourcesClassFilterAction, CreateResourceClass,
                         DeleteResourceClass)
        row_actions = (UpdateResourceClass, DeleteResourceClass)


class FlavorsFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        pass


class RacksFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        pass


class RacksTable(racks_tables.RacksTable):
    class Meta:
        name = "racks_table"
        verbose_name = _("Racks")
        table_actions = (RacksFilterAction,)


class RacksFormsetTable(tuskar_ui.tables.FormsetDataTableMixin, RacksTable):
    formset_class = forms.SelectRackFormset

    class Meta:
        name = "racks"
        verbose_name = _("Racks")
        multi_select = False
        table_actions = (RacksFilterAction,)

    def __init__(self, *args, **kwargs):
        # Adding a column at the left of the table.
        selected = tables.Column('selected', verbose_name="", sortable=False)
        selected.classes.append('narrow')
        selected.table = self
        self._columns.insert(0, 'selected', selected)
        super(RacksFormsetTable, self).__init__(*args, **kwargs)


class UpdateRacksClass(tables.LinkAction):
    name = "edit_flavors"
    verbose_name = _("Edit Racks")

    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, datum=None):
        url = ("horizon:infrastructure:resource_management:resource_classes:"
               "update_racks")
        return "%s?step=%s" % (
            urlresolvers.reverse(
                url,
                args=(self.table.kwargs['resource_class_id'],)),
            resource_classes.workflows.RacksAction.slug)


class UpdateFlavorsClass(tables.LinkAction):
    name = "edit_flavors"
    verbose_name = _("Edit Flavors")
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, datum=None):
        url = ("horizon:infrastructure:resource_management:resource_classes:"
               "update_flavors")
        resource_class_id = self.table.kwargs.get('resource_class_id')
        return "%s?step=%s" % (
            urlresolvers.reverse(url, args=(resource_class_id,)),
            resource_classes.workflows.ResourceClassFlavorsAction.slug)


class FlavorsTable(tables.DataTable):
    def get_flavor_detail_link(datum):
        # FIXME - horizon Column.get_link_url does not allow to access GET
        # params
        resource_class_id = re.findall("[0-9]+", datum.request.path)[-1]
        return urlresolvers.reverse(
            "horizon:infrastructure:resource_management:resource_classes:"
            "flavors:detail", args=(resource_class_id, datum.id))

    name = tables.Column(
        'name',
        link=get_flavor_detail_link,
        verbose_name=_('Flavor Name'),
    )
    cpu = tables.Column(
        "cpu",
        verbose_name=_('VCPU'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    memory = tables.Column(
        "memory",
        verbose_name=_('RAM (MB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    storage = tables.Column(
        "storage",
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
    max_vms = tables.Column("max_vms", verbose_name=_("Max. VMs"))

    class Meta:
        name = "flavors_table"
        verbose_name = _("Flavors")
        table_actions = (FlavorsFilterAction, UpdateFlavorsClass)


class FlavorsFormsetTable(tuskar_ui.tables.FormsetDataTableMixin,
                          FlavorsTable):

    name = tables.Column(
        'name',
        verbose_name=_('Flavor Name'),
    )
    DELETE = tables.Column('DELETE', verbose_name=_("Delete"))
    formset_class = flavors_forms.FlavorFormset

    class Meta:
        name = "flavors"
        verbose_name = _("Flavors")
        table_actions = ()
        multi_select = False
