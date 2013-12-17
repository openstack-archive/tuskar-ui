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

from heatclient.v1 import resources
from heatclient.v1 import stacks
from ironicclient.v1 import node


def data(TEST):

    # Stack
    TEST.heatclient_stacks = test_data_utils.TestDataContainer()
    stack_1 = stacks.Stack(
        stacks.StackManager(None),
        {'id': '1',
         'stack_name': 'overcloud',
         'stack_status': 'RUNNING'})
    TEST.heatclient_stacks.add(stack_1)

    # Node
    TEST.ironicclient_nodes = test_data_utils.TestDataContainer()
    node_1 = node.Node(
        node.NodeManager(None),
        {'uuid': 'aa-11',
         'instance_uuid': 'aa'})
    node_2 = node.Node(
        node.NodeManager(None),
        {'uuid': 'bb-22',
         'instance_uuid': 'bb'})
    node_3 = node.Node(
        node.NodeManager(None),
        {'uuid': 'cc-33',
         'instance_uuid': None})
    TEST.ironicclient_nodes.add(node_1, node_2, node_3)

    # Resource
    TEST.heatclient_resources = test_data_utils.TestDataContainer()
    resource_1 = resources.Resource(
        resources.ResourceManager(None),
        {'stack_id': '1',
         'resource_name': 'Compute',
         'logical_resource_id': 'Compute',
         'physical_resource_id': 'aa',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'AWS::EC2::Instance'})
    resource_2 = resources.Resource(
        resources.ResourceManager(None),
        {'stack_id': '1',
         'resource_name': 'Control',
         'logical_resource_id': 'Control',
         'physical_resource_id': 'bb',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'AWS::EC2::Instance'})
    TEST.heatclient_resources.add(resource_1, resource_2)

    # ResourceCategory
