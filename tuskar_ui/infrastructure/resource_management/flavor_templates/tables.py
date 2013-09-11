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

from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import tables

from tuskar_ui import api as tuskar
from tuskar_ui import tables as tuskar_tables


LOG = logging.getLogger(__name__)


class DeleteFlavorTemplates(tables.DeleteAction):
    data_type_singular = _("Flavor Template")
    data_type_plural = _("Flavor Templates")

    def delete(self, request, obj_id):
        tuskar.FlavorTemplate.delete(request, obj_id)


class CreateFlavorTemplate(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Flavor Template")
    url = "horizon:infrastructure:resource_management:flavor_templates:create"
    classes = ("ajax-modal", "btn-create")


class EditFlavorTemplate(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Flavor Template")
    url = "horizon:infrastructure:resource_management:flavor_templates:edit"
    classes = ("ajax-modal", "btn-edit")


class FlavorTemplatesFilterAction(tables.FilterAction):

    def filter(self, table, flavor_templates, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        return [flavor_template for flavor_template in flavor_templates
                if q in flavor_template.name.lower()]


class FlavorTemplatesTable(tuskar_tables.DataTable):
    name = tuskar_tables.Column(
        'name',
        link=("horizon:infrastructure:"
              "resource_management:flavor_templates:detail"),
        verbose_name=_('Flavor Template Name')
    )
    cpu = tuskar_tables.Column(
        "cpu",
        verbose_name=_('VCPU'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    memory = tuskar_tables.Column(
        "memory",
        verbose_name=_('RAM (MB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    storage = tuskar_tables.Column(
        "storage",
        verbose_name=_('Root Disk (GB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    ephemeral_disk = tuskar_tables.Column(
        "ephemeral_disk",
        verbose_name=_('Ephemeral Disk (GB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )
    swap_disk = tuskar_tables.Column(
        "swap_disk",
        verbose_name=_('Swap Disk (MB)'),
        filters=(lambda x: getattr(x, 'value', ''),)
    )

    class Meta:
        name = "flavor_templates"
        verbose_name = _("Flavor Templates")
        table_actions = (CreateFlavorTemplate,
                         DeleteFlavorTemplates,
                         FlavorTemplatesFilterAction)
        row_actions = (EditFlavorTemplate, DeleteFlavorTemplates)
