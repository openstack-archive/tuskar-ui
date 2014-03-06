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

from tuskar_ui import api


class CreateNodeProfile(flavor_tables.CreateFlavor):
    verbose_name = _("New Node Profile")
    url = "horizon:infrastructure:node_profiles:create"


class CreateSuggestedNodeProfile(CreateNodeProfile):
    verbose_name = _("Create")


class DeleteNodeProfile(flavor_tables.DeleteFlavor):

    def __init__(self, **kwargs):
        super(DeleteNodeProfile, self).__init__(**kwargs)
        # NOTE(dtantsur): setting class attributes doesn't work
        # probably due to metaclass magic in actions
        self.data_type_singular = _("Node Profile")
        self.data_type_plural = _("Node Profiles")

    def allowed(self, request, datum=None):
        """Check that action is allowed on node profile

        This is overridden method from horizon.tables.BaseAction.

        :param datum: node profile we're operating on
        :type  datum: tuskar_ui.api.NodeProfile
        """
        if datum is not None:
            deployed_profiles = api.NodeProfile.list_deployed_ids(
                request, _error_default=None)
            if deployed_profiles is None or datum.id in deployed_profiles:
                return False
        return super(DeleteNodeProfile, self).allowed(request, datum)


class NodeProfilesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Node Profile'),
                         link="horizon:infrastructure:node_profiles:details")
    arch = tables.Column('cpu_arch', verbose_name=_('Architecture'))
    vcpus = tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = tables.Column(flavor_tables.get_size,
                        verbose_name=_('Memory'),
                        attrs={'data-type': 'size'})
    disk = tables.Column(flavor_tables.get_disk_size,
                         verbose_name=_('Disk'),
                         attrs={'data-type': 'size'})
    # FIXME(dtantsur): would be much better to have names here
    kernel_image_id = tables.Column('kernel_image_id',
                                    verbose_name=_('Deploy Kernel Image ID'))
    ramdisk_image_id = tables.Column('ramdisk_image_id',
                                     verbose_name=_('Deploy Ramdisk Image ID'))

    class Meta:
        name = "node_profiles"
        verbose_name = _("Node Profiles")
        table_actions = (CreateNodeProfile,
                         DeleteNodeProfile,
                         flavor_tables.FlavorFilterAction)
        row_actions = (DeleteNodeProfile,)


class NodeProfileRolesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Role Name'))

    def __init__(self, request, *args, **kwargs):
        # TODO(dtantsur): support multiple overclouds
        try:
            overcloud = api.Overcloud.get_the_overcloud(request)
        except Exception:
            count_getter = lambda role: _("Not deployed")
        else:
            count_getter = overcloud.resources_count
        self._columns['count'] = tables.Column(
            count_getter,
            verbose_name=_("Instances Count")
        )
        super(NodeProfileRolesTable, self).__init__(request, *args, **kwargs)


class ProfileSuggestionsTable(tables.DataTable):
    arch = tables.Column('cpu_arch', verbose_name=_('Architecture'))
    vcpus = tables.Column('vcpus', verbose_name=_('CPUs'))
    ram = tables.Column(
        lambda p: '%dMB' % (p.ram / 1024 / 1024),
        verbose_name=_('Memory'),
        attrs={'data-type': 'size'},
    )
    disk = tables.Column(
        lambda p: '%sGB' % (p.disk / 1024 / 1024 / 1024),
        verbose_name=_('Disk'),
        attrs={'data-type': 'size'},
    )

    class Meta:
        name = "profile_suggestions"
        verbose_name = _("Profile Suggestions")
        table_actions = ()
        row_actions = (CreateSuggestedNodeProfile,)
