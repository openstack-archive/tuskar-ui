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

from novaclient.v2 import flavors
from openstack_dashboard.test.test_data import utils as test_data_utils


def data(TEST):

    # Nova flavors
    # Do not include fields irrelevant for our usage
    TEST.novaclient_flavors = test_data_utils.TestDataContainer()
    flavor_1 = flavors.Flavor(
        flavors.FlavorManager(None),
        {'id': '1',
         'name': 'flavor-1',
         'vcpus': 2,
         'ram': 2048,
         'disk': 20})
    flavor_1.get_keys = lambda: {'cpu_arch': 'amd64'}
    flavor_2 = flavors.Flavor(
        flavors.FlavorManager(None),
        {'id': '2',
         'name': 'flavor-2',
         'vcpus': 4,
         'ram': 4096,
         'disk': 60})
    flavor_2.get_keys = lambda: {'cpu_arch': 'i386'}
    TEST.novaclient_flavors.add(flavor_1, flavor_2)
