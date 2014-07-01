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
#from openstack_dashboard.api import nova
from openstack_dashboard.test.test_data import utils as test_utils

#from tuskar_ui.api import tuskar
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.test.test_data import flavor_data
from tuskar_ui.test.test_data import heat_data


TEST_DATA = test_utils.TestDataContainer()
flavor_data.data(TEST_DATA)
heat_data.data(TEST_DATA)

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
               kernel_image_id, ramdisk_image_id):
        return cls(TEST_DATA.novaclient_flavors.first(),
                   request=request)

    @classmethod
    @handle_errors(_("Unable to load flavor."))
    def get(cls, request, flavor_id):
        for flavor in Flavor.list(request):
            if flavor.id == flavor_id:
                return flavor

    @classmethod
    @handle_errors(_("Unable to retrieve flavor list."), [])
    def list(cls, request):
        flavors = TEST_DATA.novaclient_flavors.list()
        return [cls(flavor) for flavor in flavors]

    @classmethod
    @memoized.memoized
    @handle_errors(_("Unable to retrieve existing servers list."), [])
    def list_deployed_ids(cls, request):
        """Get and memoize ID's of deployed flavors."""
        servers = TEST_DATA.novaclient_servers.list()
        deployed_ids = set(server.flavor['id'] for server in servers)
        return deployed_ids
