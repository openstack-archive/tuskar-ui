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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables

from tuskar_ui import api
import tuskar_ui.tables
from tuskar_ui.forms import NumberInput

from tuskar_ui.infrastructure. \
    resource_management.flavors import tables as flavors_tables
from tuskar_ui.infrastructure. \
    resource_management.racks import tables as racks_tables
from tuskar_ui.infrastructure. \
    resource_management import resource_classes


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
            api.tuskar.ResourceClass.delete(request, obj_id)
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
    nodes_count = tables.Column("nodes_count",
                                verbose_name=_("Nodes"),
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


class FlavorsTable(flavors_tables.FlavorsTable):
    name = tables.Column('name',
                         verbose_name=_('Flavor Name'))
    max_vms = tuskar_ui.tables.Column("max_vms",
                            auto='form_widget',
                            verbose_name=_("Max. VMs"),
                            form_widget=NumberInput(),
                            form_widget_attributes={
                                'class': "number_input_slim"})

    class Meta:
        name = "flavors"
        verbose_name = _("Flavors")
        multi_select = True
        multi_select_name = "flavors_object_ids"


class RacksFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        pass


class RacksTable(racks_tables.RacksTable):

    class Meta:
        name = "racks"
        verbose_name = _("Racks")
        multi_select = True
        multi_select_name = "racks_object_ids"
        table_actions = (RacksFilterAction,)


class UpdateRacksClass(tables.LinkAction):
    name = "edit_flavors"
    verbose_name = _("Edit Racks")

    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, datum=None):
        url = "horizon:infrastructure:resource_management:resource_classes:"\
              "update_racks"
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
        url = "horizon:infrastructure:resource_management:resource_classes:"\
              "update_flavors"
        return "%s?step=%s" % (
            urlresolvers.reverse(
                url,
                args=(self.table.kwargs['resource_class_id'],)),
            resource_classes.workflows.ResourceClassInfoAndFlavorsAction.slug)


class ResourceClassDetailFlavorsTable(flavors_tables.FlavorsTable):
    max_vms = tables.Column("max_vms",
                            verbose_name=_("Max. VMs"))

    class Meta:
        name = "flavors"
        verbose_name = _("Flavors")
        table_actions = (FlavorsFilterAction, UpdateFlavorsClass)
