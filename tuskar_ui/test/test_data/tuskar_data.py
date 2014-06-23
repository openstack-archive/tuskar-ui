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

from openstack_dashboard.test.test_data import utils as test_data_utils

from tuskarclient.v1 import overcloud_roles
from tuskarclient.v1 import overclouds


def data(TEST):

    # Overcloud
    TEST.tuskarclient_overcloud_plans = test_data_utils.TestDataContainer()
    # TODO(Tzu-Mainn Chen): fix these to create Tuskar Overcloud objects
    # once the api supports it
    oc_1 = overclouds.Overcloud(
        overclouds.OvercloudManager(None),
        {'id': 1,
         'name': 'overcloud',
         'description': 'overcloud',
         'stack_id': 'stack-id-1',
         'attributes': {
             'AdminPassword': "unset"
         }})
    TEST.tuskarclient_overcloud_plans.add(oc_1)

    # OvercloudRole
    TEST.tuskarclient_overcloud_roles = test_data_utils.TestDataContainer()
    r_1 = overcloud_roles.OvercloudRole(
        overcloud_roles.OvercloudRoleManager(None),
        {
            'id': 1,
            'name': 'Controller',
            'description': 'controller overcloud role',
            'image_name': 'overcloud-control',
            'flavor_id': '',
        })
    r_2 = overcloud_roles.OvercloudRole(
        overcloud_roles.OvercloudRoleManager(None),
        {'id': 2,
         'name': 'Compute',
         'description': 'compute overcloud role',
         'flavor_id': '',
         'image_name': 'overcloud-compute'})
    r_3 = overcloud_roles.OvercloudRole(
        overcloud_roles.OvercloudRoleManager(None),
        {'id': 3,
         'name': 'Object Storage',
         'description': 'object storage overcloud role',
         'flavor_id': '',
         'image_name': 'overcloud-object-storage'})
    r_4 = overcloud_roles.OvercloudRole(
        overcloud_roles.OvercloudRoleManager(None),
        {'id': 4,
         'name': 'Block Storage',
         'description': 'block storage overcloud role',
         'flavor_id': '',
         'image_name': 'overcloud-block-storage'})
    TEST.tuskarclient_overcloud_roles.add(r_1, r_2, r_3, r_4)

    # OvercloudRoles with flavors associated
    TEST.tuskarclient_roles_with_flavors = test_data_utils.TestDataContainer()
    role_with_flavor = overcloud_roles.OvercloudRole(
        overcloud_roles.OvercloudRoleManager(None),
        {'id': 5,
         'name': 'Block Storage',
         'description': 'block storage overcloud role',
         'flavor_id': '1',
         'image_name': 'overcloud-block-storage'})
    TEST.tuskarclient_roles_with_flavors.add(role_with_flavor)
