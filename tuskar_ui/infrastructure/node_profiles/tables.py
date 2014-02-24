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
from horizon.utils import memoized

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


@memoized.memoized
def memoized_extras(flavor):
    return flavor.get_keys()


def extras_getter(key):
    return lambda flavor: memoized_extras(flavor).get(key, '')


class NodeProfilesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Node'))
    arch = tables.Column(extras_getter('cpu_arch'),
                         verbose_name=_('Architecture'))
    vcpus = tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = tables.Column(flavor_tables.get_size,
                        verbose_name=_('Memory'),
                        attrs={'data-type': 'size'})
    disk = tables.Column(flavor_tables.get_disk_size,
                         verbose_name=_('Disk'),
                         attrs={'data-type': 'size'})
    # FIXME(dtantsur): would be much better to have names here
    kernel_id = tables.Column(extras_getter('baremetal:deploy_kernel_id'),
                              verbose_name=_('Deploy Kernel Image ID'))
    ramdisk_id = tables.Column(extras_getter('baremetal:deploy_ramdisk_id'),
                               verbose_name=_('Deploy Ramdisk Image ID'))

    class Meta:
        name = "node_profiles"
        verbose_name = _("Node Profiles")
        table_actions = (CreateNodeProfile,
                         DeleteNodeProfile,
                         flavor_tables.FlavorFilterAction)
        row_actions = (DeleteNodeProfile,)
