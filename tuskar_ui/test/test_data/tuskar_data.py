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
            'name': 'Controller-1::count',
            'label': 'Controller Node Count',
            'description': 'Controller node count',
            'hidden': 'false',
            'value': 1,
        }, {
            'name': 'Compute-1::count',
            'label': 'Compute Node Count',
            'description': 'Compute node count',
            'hidden': 'false',
            'value': 42,
        }, {
            'name': 'Block Storage-1::count',
            'label': 'Block Sorage Node Count',
            'description': 'Block storage node count',
            'hidden': 'false',
            'value': 5,
        }, {
            'name': 'Controller-1::instance_type',
            'label': 'Controller Instance Type',
            'description': 'Controller instance type',
            'hidden': 'false',
            'value': 'flavor-1',
        }, {
            'name': 'Compute-1::instance_type',
            'label': 'Compute Instance Type',
            'description': 'Compute instance type',
            'hidden': 'false',
            'value': 'flavor-1',
        }, {
            'name': 'Block Storage-1::instance_type',
            'label': 'Block Storage Instance Type',
            'description': 'Block storage instance type',
            'hidden': 'false',
            'value': 'flavor-2',
        }, {
            'name': 'Controller-1::image_id',
            'label': 'Controller Image ID',
            'description': 'Controller image ID',
            'hidden': 'false',
            'value': '2',
        }, {
            'name': 'Compute-1::image_id',
            'label': 'Compute Image ID',
            'description': 'Compute image ID',
            'hidden': 'false',
            'value': '1',
        }, {
            'name': 'Block Storage-1::image_id',
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
            'value': '5ba3a69c95c668daf84c2f103ebec82d273a4897',
        }, {
            'name': 'AdminToken',
            'label': 'Admin Token',
            'description': 'Admin Token',
            'hidden': 'false',
            'value': 'aa61677c0a270880e99293c148cefee4000b2259',
        }, {
            'name': 'GlancePassword',
            'label': 'Glance Password',
            'description': 'Glance Password',
            'hidden': 'false',
            'value': '16b4aaa3e056d07f796a93afb6010487b7b617e7',
        }, {
            'name': 'NovaPassword',
            'label': 'Nova Password',
            'description': 'Nova Password',
            'hidden': 'false',
            'value': '67d8090ff40c0c400b08ff558233091402afc9c5',
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
