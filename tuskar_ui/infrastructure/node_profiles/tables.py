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

from openstack_dashboard.dashboards.admin.flavors \
    import tables as flavor_tables


class CreateNodeProfile(flavor_tables.CreateFlavor):
    verbose_name = _("New Node Profile")
    url = "horizon:infrastructure:node_profiles:create"


class DeleteNodeProfile(flavor_tables.DeleteFlavor):

    def __init__(self, **kwargs):
        super(DeleteNodeProfile, self).__init__(**kwargs)
        # NOTE(dtantsur): setting class attributes doesn't work
        # probably due to metaclass magic in actions
        self.data_type_singular = _("Node Profile")
        self.data_type_plural = _("Node Profiles")


def get_arch(flavor):
    extra_specs = flavor.get_keys()
    return extra_specs.get('cpu_arch', '')


class NodeProfilesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Node'))
    arch = tables.Column(get_arch, verbose_name=_('Architecture'))
    vcpus = tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = tables.Column(flavor_tables.get_size,
                        verbose_name=_('Memory'),
                        attrs={'data-type': 'size'})
    disk = tables.Column(flavor_tables.get_disk_size,
                         verbose_name=_('Disk'),
                         attrs={'data-type': 'size'})

    class Meta:
        name = "node_profiles"
        verbose_name = _("Node Profiles")
        table_actions = (CreateNodeProfile,
                         DeleteNodeProfile,
                         flavor_tables.FlavorFilterAction)
        row_actions = (DeleteNodeProfile,)
