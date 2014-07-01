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


def data(TEST):

    # OvercloudPlan
    TEST.tuskarclient_plans = test_data_utils.TestDataContainer()
    plan_1 = {
        'id': 'plan-1',
        'name': 'overcloud',
        'description': 'this is an overcloud deployment plan',
        'created_at': '2014-05-27T21:11:09Z',
        'modified_at': '2014-05-30T21:11:09Z',
        'roles': [{
            'id': 'role-1',
            'name': 'Controller',
            'version': 1,
        }, {
            'id': 'role-2',
            'name': 'Compute',
            'version': 1,
        }, {
            'id': 'role-3',
            'name': 'Object Storage',
            'version': 1,
        }, {
            'id': 'role-5',
            'name': 'Block Storage',
            'version': 2,
        }],
        'parameters': [{
            'name': 'AdminPassword',
            'label': 'Admin Password',
            'description': 'Admin password',
            'hidden': 'false',
            'value': 'unset',
        }],
    }
    TEST.tuskarclient_plans.add(plan_1)

    # OvercloudRole
    TEST.tuskarclient_roles = test_data_utils.TestDataContainer()
    r_1 = {
        'id': 'role-1',
        'name': 'Controller',
        'version': 1,
        'description': 'controller role',
        'created_at': '2014-05-27T21:11:09Z',
    }
    r_2 = {
        'id': 'role-2',
        'name': 'Compute',
        'version': 1,
        'description': 'compute role',
        'created_at': '2014-05-27T21:11:09Z',
    }
    r_3 = {
        'id': 'role-3',
        'name': 'Object Storage',
        'version': 1,
        'description': 'object storage role',
        'created_at': '2014-05-27T21:11:09Z',
    }
    r_4 = {
        'id': 'role-4',
        'name': 'Block Storage',
        'version': 1,
        'description': 'block storage role',
        'created_at': '2014-05-27T21:11:09Z',
    }
    r_5 = {
        'id': 'role-5',
        'name': 'Block Storage',
        'version': 2,
        'description': 'block storage role',
        'created_at': '2014-05-28T21:11:09Z',
    }
    TEST.tuskarclient_roles.add(r_1, r_2, r_3, r_4, r_5)
