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

from django.utils.translation import ugettext_lazy as _
from horizon.utils import memoized
from openstack_dashboard.api import nova

import tuskar_ui
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa


LOG = logging.getLogger(__name__)


class Flavor(object):

    def __init__(self, flavor):
        """Construct by wrapping Nova flavor

        :param flavor: Nova flavor
        :type  flavor: novaclient.v1_1.flavors.Flavor
        """
        self._flavor = flavor

    def __getattr__(self, name):
        return getattr(self._flavor, name)

    @property
    def ram_bytes(self):
        """Get RAM size in bytes

        Default RAM size is in MB.
        """
        return self.ram * 1024 * 1024

    @property
    def disk_bytes(self):
        """Get disk size in bytes

        Default disk size is in GB.
        """
        return self.disk * 1024 * 1024 * 1024

    @cached_property
    def extras_dict(self):
        """Return extra flavor parameters

        :return: Nova flavor keys
        :rtype: dict
        """
        return self._flavor.get_keys()

    @property
    def cpu_arch(self):
        return self.extras_dict.get('cpu_arch', '')

    @property
    def kernel_image_id(self):
        return self.extras_dict.get('baremetal:deploy_kernel_id', '')

    @property
    def ramdisk_image_id(self):
        return self.extras_dict.get('baremetal:deploy_ramdisk_id', '')

    @classmethod
    def create(cls, request, name, memory, vcpus, disk, cpu_arch,
               kernel_image_id=None, ramdisk_image_id=None):
        extras_dict = {'cpu_arch': cpu_arch}
        if kernel_image_id is not None:
            extras_dict['baremetal:deploy_kernel_id'] = kernel_image_id
        if ramdisk_image_id is not None:
            extras_dict['baremetal:deploy_ramdisk_id'] = ramdisk_image_id
        return cls(nova.flavor_create(request, name, memory, vcpus, disk,
                                      metadata=extras_dict))

    @classmethod
    @handle_errors(_("Unable to load flavor."))
    def get(cls, request, flavor_id):
        return cls(nova.flavor_get(request, flavor_id))

    @classmethod
    @handle_errors(_("Unable to load flavor."))
    def get_by_name(cls, request, name):
        for flavor in cls.list(request):
            if flavor.name == name:
                return flavor

    @classmethod
    @handle_errors(_("Unable to retrieve flavor list."), [])
    def list(cls, request):
        return [cls(item) for item in nova.flavor_list(request)]

    @classmethod
    @memoized.memoized
    @handle_errors(_("Unable to retrieve existing servers list."), [])
    def list_deployed_ids(cls, request):
        """Get and memoize ID's of deployed flavors."""
        servers = nova.server_list(request)[0]
        deployed_ids = set(server.flavor['id'] for server in servers)
        deployed_names = []
        for plan in tuskar_ui.api.tuskar.Plan.list(request):
            deployed_names.extend(
                [plan.parameter_value(role.flavor_parameter_name)
                 for role in plan.role_list])
        return [flavor.id for flavor in cls.list(request)
                if flavor.id in deployed_ids or flavor.name in deployed_names]
