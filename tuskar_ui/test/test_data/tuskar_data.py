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
from ironicclient.v1 import port


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
         'instance_uuid': 'aa',
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '1.1.1.1',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
         },
         'properties': {
             'cpu': '8',
             'ram': '16',
             'local_disk': '10',
         },
         'power_state': 'on'})
    node_2 = node.Node(
        node.NodeManager(None),
        {'uuid': 'bb-22',
         'instance_uuid': 'bb',
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '2.2.2.2',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
         },
         'properties': {
             'cpu': '16',
             'ram': '32',
             'local_disk': '100',
         },
         'power_state': 'on'})
    node_3 = node.Node(
        node.NodeManager(None),
        {'uuid': 'cc-33',
         'instance_uuid': None,
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '3.3.3.3',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
         },
         'properties': {
             'cpu': '32',
             'ram': '64',
             'local_disk': '1',
         },
         'power_state': 'rebooting'})
    TEST.ironicclient_nodes.add(node_1, node_2, node_3)

    # Ports
    TEST.ironicclient_ports = test_data_utils.TestDataContainer()
    port_1 = port.Port(
        port.PortManager(None),
        {'id': '1-port-id',
         'type': 'port',
         'address': 'aa:aa:aa:aa:aa:aa'})
    port_2 = port.Port(
        port.PortManager(None),
        {'id': '2-port-id',
         'type': 'port',
         'address': 'bb:bb:bb:bb:bb:bb'})
    port_3 = port.Port(
        port.PortManager(None),
        {'id': '3-port-id',
         'type': 'port',
         'address': 'cc:cc:cc:cc:cc:cc'})
    port_4 = port.Port(
        port.PortManager(None),
        {'id': '4-port-id',
         'type': 'port',
         'address': 'dd:dd:dd:dd:dd:dd'})
    TEST.ironicclient_ports.add(port_1, port_2, port_3, port_4)

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
