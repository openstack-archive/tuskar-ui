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
import django.shortcuts
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.messages
import horizon.tables
from openstack_dashboard.api import glance
from openstack_dashboard.dashboards.admin.flavors import (
    tables as flavor_tables)

from tuskar_ui import api
from tuskar_ui.infrastructure.flavors import utils
import tuskar_ui.utils.utils

DEFAULT_KERNEL_IMAGE_NAME = 'discovery-kernel'
DEFAULT_RAMDISK_IMAGE_NAME = 'discovery-ramdisk'


def _guess_default_image_ids(request):
    try:
        images = glance.image_list_detailed(request)[0]
    except Exception:
        horizon.exceptions.handle(request,
                                  _('Unable to retrieve images list.'))
        kernel_images = []
        ramdisk_images = []
    else:
        has_type = tuskar_ui.utils.utils.check_image_type
        kernel_images = [
            image for image in images
            if has_type(image, 'discovery kernel')
            and image.name == DEFAULT_KERNEL_IMAGE_NAME
        ]
        ramdisk_images = [
            image for image in images
            if has_type(image, 'discovery ramdisk')
            and image.name == DEFAULT_RAMDISK_IMAGE_NAME
        ]
    if not kernel_images or not ramdisk_images:
        raise ValueError("No default images")
    return kernel_images[0].id, ramdisk_images[0].id


class CreateFlavor(flavor_tables.CreateFlavor):
    verbose_name = _(u"New Flavor")
    url = "horizon:infrastructure:flavors:create"


class CreateSuggestedFlavor(horizon.tables.Action):
    name = 'create'
    verbose_name = _(u"Create")
    verbose_name_plural = _(u"Create Suggested Flavors")
    method = 'POST'
    icon = 'plus'

    def create_flavor(self, request, node_id, images):
        node = api.node.Node.get(request, node_id)
        suggestion = utils.FlavorSuggestion.from_node(node)
        return suggestion.create_flavor(request, *images)

    def handle(self, data_table, request, node_ids):
        try:
            images = _guess_default_image_ids(request)
        except ValueError:
            horizon.messages.error(request, _(
                "No default images available. "
                "Create images called \"{0}\" and \"{1}\" or "
                "use the \"{2}\" action to choose different image names."
            ).format(
                DEFAULT_KERNEL_IMAGE_NAME,
                DEFAULT_RAMDISK_IMAGE_NAME,
                EditAndCreateSuggestedFlavor.verbose_name,
            ))
        else:
            for node_id in node_ids:
                try:
                    self.create_flavor(request, node_id, images)
                except Exception:
                    horizon.exceptions.handle(request,
                        _(u"Unable to create flavor for node %r") % node_id,)
        return django.shortcuts.redirect(request.get_full_path())


class EditAndCreateSuggestedFlavor(CreateFlavor):
    name = 'edit_and_create'
    verbose_name = _(u"Edit before creating")
    icon = 'pencil'


class DeleteFlavor(flavor_tables.DeleteFlavor):

    def __init__(self, **kwargs):
        super(DeleteFlavor, self).__init__(**kwargs)
        # NOTE(dtantsur): setting class attributes doesn't work
        # probably due to metaclass magic in actions
        self.data_type_singular = _("Flavor")
        self.data_type_plural = _("Flavors")

    def allowed(self, request, datum=None):
        """Check that action is allowed on flavor

        This is overridden method from horizon.tables.BaseAction.

        :param datum: flavor we're operating on
        :type  datum: tuskar_ui.api.Flavor
        """
        if datum is not None:
            deployed_flavors = api.flavor.Flavor.list_deployed_ids(
                request, _error_default=None)
            if deployed_flavors is None or datum.id in deployed_flavors:
                return False
        return super(DeleteFlavor, self).allowed(request, datum)


class FlavorsTable(horizon.tables.DataTable):
    name = horizon.tables.Column('name',
                                 link="horizon:infrastructure:flavors:details")
    arch = horizon.tables.Column('cpu_arch', verbose_name=_('Architecture'))
    vcpus = horizon.tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = horizon.tables.Column(flavor_tables.get_size,
                                verbose_name=_('Memory'),
                                attrs={'data-type': 'size'})
    disk = horizon.tables.Column(flavor_tables.get_disk_size,
                                 verbose_name=_('Disk'),
                                 attrs={'data-type': 'size'})

    class Meta:
        name = "flavors"
        verbose_name = _("Available")
        table_actions = (
            DeleteFlavor,
            flavor_tables.FlavorFilterAction,
        )
        row_actions = (
            DeleteFlavor,
        )
        template = "horizon/common/_enhanced_data_table.html"


class FlavorRolesTable(horizon.tables.DataTable):
    name = horizon.tables.Column('name', verbose_name=_('Role Name'))

    def __init__(self, request, *args, **kwargs):
        # TODO(dtantsur): support multiple overclouds
        plan = api.tuskar.Plan.get_the_plan(request)
        stack = api.heat.Stack.get_by_plan(request, plan)

        if stack is None:
            count = lambda role: _('Not Deployed')
        else:
            count = stack.resources_count

        self._columns['count'] = horizon.tables.Column(
            count,
            verbose_name=_("Instances Count")
        )
        super(FlavorRolesTable, self).__init__(request, *args, **kwargs)

    class Meta:
        name = "flavor_roles"
        verbose_name = _("Overcloud Roles")
        table_actions = ()
        row_actions = ()
        hidden_title = False
        template = "horizon/common/_enhanced_data_table.html"


class FlavorSuggestionsTable(horizon.tables.DataTable):
    name = horizon.tables.Column('name',)
    arch = horizon.tables.Column('cpu_arch', verbose_name=_('Architecture'))
    vcpus = horizon.tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = horizon.tables.Column(flavor_tables.get_size,
                                verbose_name=_('Memory'),
                                attrs={'data-type': 'size'})
    disk = horizon.tables.Column(flavor_tables.get_disk_size,
                                 verbose_name=_('Disk'),
                                 attrs={'data-type': 'size'})

    class Meta:
        name = "suggested_flavors"
        verbose_name = _("Suggested")
        row_actions = (
            CreateSuggestedFlavor,
            EditAndCreateSuggestedFlavor,
        )
        template = "horizon/common/_enhanced_data_table.html"
