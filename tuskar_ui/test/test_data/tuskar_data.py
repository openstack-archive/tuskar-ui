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
from tuskarclient.v2 import plans
from tuskarclient.v2 import roles

planmanager = plans.PlanManager(None)
rolemanager = roles.RoleManager(None)


def data(TEST):

    # Plan
    TEST.tuskarclient_plans = test_data_utils.TestDataContainer()
    plan_1 = plans.Plan(planmanager, {
        'id': 'plan-1',
        'name': 'overcloud',
        'description': 'this is an overcloud deployment plan',
        'template': '',
        'created_at': '2014-05-27T21:11:09Z',
        'modified_at': '2014-05-30T21:11:09Z',
        'roles': [
            {
                'uuid': 'role-1',
                'name': 'Controller',
                'version': 1,
            }, {
                'uuid': 'role-2',
                'name': 'Compute',
                'version': 1,
            }, {
                'uuid': 'role-3',
                'name': 'Object Storage',
                'version': 1,
            }, {
                'uuid': 'role-4',
                'name': 'Block Storage',
                'version': 1,
            }],
        'parameters': [{
            'name': 'ControllerNodeCount',
            'label': 'Controller Node Count',
            'description': 'Controller node count',
            'hidden': 'false',
            'value': 1,
        }, {
            'name': 'ComputeNodeCount',
            'label': 'Compute Node Count',
            'description': 'Compute node count',
            'hidden': 'false',
            'value': 42,
        }, {
            'name': 'Block StorageNodeCount',
            'label': 'Block Sorage Node Count',
            'description': 'Block storage node count',
            'hidden': 'false',
            'value': 5,
        }, {
            'name': 'ControllerFlavorID',
            'label': 'Controller Flavor ID',
            'description': 'Controller flavor ID',
            'hidden': 'false',
            'value': '1',
        }, {
            'name': 'ComputeFlavorID',
            'label': 'Compute Flavor ID',
            'description': 'Compute flavor ID',
            'hidden': 'false',
            'value': '1',
        }, {
            'name': 'Block StorageFlavorID',
            'label': 'Block Storage Flavor ID',
            'description': 'Block storage flavor ID',
            'hidden': 'false',
            'value': '2',
        }, {
            'name': 'ControllerImageID',
            'label': 'Controller Image ID',
            'description': 'Controller image ID',
            'hidden': 'false',
            'value': '2',
        }, {
            'name': 'ComputeImageID',
            'label': 'Compute Image ID',
            'description': 'Compute image ID',
            'hidden': 'false',
            'value': '1',
        }, {
            'name': 'Block StorageImageID',
            'label': 'Block Storage Image ID',
            'description': 'Block storage image ID',
            'hidden': 'false',
            'value': '4',
        }, {
            'name': 'controller_NovaInterfaces',
            'parameter_group': 'Nova',
            'type': 'String',
            'description': '',
            'no_echo': 'false',
            'default': 'eth0',
        }, {
            'name': 'controller_NeutronInterfaces',
            'parameter_group': 'Neutron',
            'type': 'String',
            'description': '',
            'no_echo': 'false',
            'default': 'eth0',
        }, {
            'name': 'compute_KeystoneHost',
            'parameter_group': 'Keystone',
            'type': 'String',
            'description': '',
            'no_echo': 'false',
            'default': '',
        }, {
            'name': 'object_storage_SwiftHashSuffix',
            'parameter_group': 'Swift',
            'type': 'String',
            'description': '',
            'no_echo': 'true',
            'default': '',
        }, {
            'name': 'block_storage_NeutronNetworkType',
            'parameter_group': 'Neutron',
            'type': 'String',
            'description': '',
            'no_echo': 'false',
            'default': 'gre',
        }, {
            'name': 'AdminPassword',
            'label': 'Admin Password',
            'description': 'Admin password',
            'hidden': 'false',
            'value': 'unset',
        }],
    })
    TEST.tuskarclient_plans.add(plan_1)

    # Role
    TEST.tuskarclient_roles = test_data_utils.TestDataContainer()
    r_1 = roles.Role(rolemanager, {
        'uuid': 'role-1',
        'name': 'Controller',
        'version': 1,
        'description': 'controller role',
        'created_at': '2014-05-27T21:11:09Z'
    })
    r_2 = roles.Role(rolemanager, {
        'uuid': 'role-2',
        'name': 'Compute',
        'version': 1,
        'description': 'compute role',
        'created_at': '2014-05-27T21:11:09Z'
    })
    r_3 = roles.Role(rolemanager, {
        'uuid': 'role-3',
        'name': 'Object Storage',
        'version': 1,
        'description': 'object storage role',
        'created_at': '2014-05-27T21:11:09Z'
    })
    r_4 = roles.Role(rolemanager, {
        'uuid': 'role-4',
        'name': 'Block Storage',
        'version': 1,
        'description': 'block storage role',
        'created_at': '2014-05-27T21:11:09Z'
    })
    TEST.tuskarclient_roles.add(r_1, r_2, r_3, r_4)
