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
        'uuid': 'plan-1',
        'name': 'overcloud',
        'description': 'this is an overcloud deployment plan',
        'template': '',
        'created_at': '2014-05-27T21:11:09Z',
        'modified_at': '2014-05-30T21:11:09Z',
        'uuid': '1234567890',
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
            'hidden': False,
            'value': 1,
        }, {
            'name': 'Compute-1::count',
            'label': 'Compute Node Count',
            'description': 'Compute node count',
            'hidden': False,
            'value': 42,
        }, {
            'name': 'Block Storage-1::count',
            'label': 'Block Sorage Node Count',
            'description': 'Block storage node count',
            'hidden': False,
            'value': 5,
        }, {
            'name': 'Controller-1::Flavor',
            'label': 'Controller Flavor',
            'description': 'Controller flavor',
            'hidden': False,
            'value': 'flavor-1',
        }, {
            'name': 'Compute-1::Flavor',
            'label': 'Compute Flavor',
            'description': 'Compute flavor',
            'hidden': False,
            'value': 'flavor-1',
        }, {
            'name': 'Block Storage-1::Flavor',
            'label': 'Block Storage Flavor',
            'description': 'Block storage flavor',
            'hidden': False,
            'value': 'flavor-2',
        }, {
            'name': 'Controller-1::Image',
            'label': 'Controller Image ID',
            'description': 'Controller image ID',
            'hidden': False,
            'value': '2',
        }, {
            'name': 'Compute-1::Image',
            'label': 'Compute Image ID',
            'description': 'Compute image ID',
            'hidden': False,
            'value': '1',
        }, {
            'name': 'Block Storage-1::Image',
            'label': 'Block Storage Image ID',
            'description': 'Block storage image ID',
            'hidden': False,
            'value': '4',
        }, {
            'name': 'Controller-1::KeystoneCACertificate',
            'label': 'Keystone CA CertificateAdmin',
            'description': 'Keystone CA CertificateAdmin',
            'hidden': True,
            'value': 'unset',
        }, {
            'name': 'Controller-1::AdminPassword',
            'label': 'Admin Password',
            'description': 'Admin password',
            'hidden': True,
            'value': 'unset',
        }, {
            'name': 'Controller-1::AdminToken',
            'label': 'Admin Token',
            'description': 'Admin Token',
            'hidden': True,
            'value': '',
        }, {
            'name': 'Controller-1::SnmpdReadonlyUserPassword',
            'label': 'Snmpd password',
            'description': 'Snmpd password',
            'hidden': True,
            'value': '',
        }, {
            'name': 'Compute-1::SnmpdReadonlyUserPassword',
            'label': 'Snmpd password',
            'description': 'Snmpd password',
            'hidden': True,
            'value': 'unset',
        }, {
            'name': 'Controller-1::ExtraConfig',
            'label': 'Extra Config',
            'description': 'Extra Config',
            'hidden': False,
            'value': '{}',
        }, {
            'name': 'Compute-1::ExtraConfig',
            'label': 'Extra Config',
            'description': 'Extra Config',
            'hidden': False,
            'value': '{}',
        }, {
            'name': 'Block Storage-1::ExtraConfig',
            'label': 'Extra Config',
            'description': 'Extra Config',
            'hidden': False,
            'value': '{}',
        }, {
            'name': 'Object Storage-1::ExtraConfig',
            'label': 'Extra Config',
            'description': 'Extra Config',
            'hidden': False,
            'value': '{}',
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
