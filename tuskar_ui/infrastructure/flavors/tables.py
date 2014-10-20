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
from openstack_dashboard.dashboards.admin.flavors import (
    tables as flavor_tables)

from tuskar_ui import api


class CreateFlavor(flavor_tables.CreateFlavor):
    verbose_name = _("New Flavor")
    url = "horizon:infrastructure:flavors:create"


class CreateSuggestedFlavor(CreateFlavor):
    verbose_name = _("Create")


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


class FlavorsTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Flavor'),
                         link="horizon:infrastructure:flavors:details")
    arch = tables.Column('cpu_arch', verbose_name=_('Architecture'))
    vcpus = tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = tables.Column(flavor_tables.get_size,
                        verbose_name=_('Memory'),
                        attrs={'data-type': 'size'})
    disk = tables.Column(flavor_tables.get_disk_size,
                         verbose_name=_('Disk'),
                         attrs={'data-type': 'size'})

    class Meta:
        name = "flavors"
        verbose_name = _("Available")
        table_actions = (CreateFlavor,
                         DeleteFlavor,
                         flavor_tables.FlavorFilterAction)
        row_actions = (DeleteFlavor,)
        template = "horizon/common/_enhanced_data_table.html"


class FlavorRolesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Role Name'))

    def __init__(self, request, *args, **kwargs):
        # TODO(dtantsur): support multiple overclouds
        try:
            stack = api.tuskar.Plan.get_the_plan(request).stack
        except Exception:
            count_getter = lambda role: _("Not deployed")
        else:
            count_getter = stack.resources_count
        self._columns['count'] = tables.Column(
            count_getter,
            verbose_name=_("Instances Count")
        )
        super(FlavorRolesTable, self).__init__(request, *args, **kwargs)

    class Meta:
        name = "flavor_roles"
        verbose_name = _("Overcloud Roles")
        table_actions = ()
        row_actions = ()
        template = "horizon/common/_enhanced_data_table.html"


class FlavorSuggestionsTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Suggested Name'))
    arch = tables.Column('cpu_arch', verbose_name=_('Architecture'))
    vcpus = tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = tables.Column(flavor_tables.get_size, verbose_name=_('Memory'),
                        attrs={'data-type': 'size'})
    disk = tables.Column(flavor_tables.get_disk_size,
                         verbose_name=_('Disk'), attrs={'data-type': 'size'})

    class Meta:
        name = "flavor_suggestions"
        verbose_name = _("Flavor Suggestions")
        table_actions = ()
        row_actions = (CreateSuggestedFlavor,)
        template = "horizon/common/_enhanced_data_table.html"
