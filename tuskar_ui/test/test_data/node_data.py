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

from ironicclient.v1 import node
from ironicclient.v1 import port
from openstack_dashboard.test.test_data import utils as test_data_utils


def data(TEST):
    # IronicNode
    TEST.ironicclient_nodes = test_data_utils.TestDataContainer()
    node_1 = node.Node(
        node.NodeManager(None),
        {'id': '1',
         'uuid': 'aa-11',
         'instance_uuid': 'aa',
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '1.1.1.1',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.2',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'maintenance': None,
         'newly_discovered': None,
         'provision_state': 'active',
         'extra': {}
         })
    node_2 = node.Node(
        node.NodeManager(None),
        {'id': '2',
         'uuid': 'bb-22',
         'instance_uuid': 'bb',
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '2.2.2.2',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.3',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '16',
             'memory_mb': '4096',
             'local_gb': '100',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'maintenance': None,
         'newly_discovered': None,
         'provision_state': 'active',
         'extra': {}
         })
    node_3 = node.Node(
        node.NodeManager(None),
        {'id': '3',
         'uuid': 'cc-33',
         'instance_uuid': 'cc',
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '3.3.3.3',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.4',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '32',
             'memory_mb': '8192',
             'local_gb': '1',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'rebooting',
         'target_power_state': 'on',
         'maintenance': None,
         'newly_discovered': None,
         'provision_state': 'deploying',
         'extra': {}
         })
    node_4 = node.Node(
        node.NodeManager(None),
        {'id': '4',
         'uuid': 'cc-44',
         'instance_uuid': 'cc',
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '4.4.4.4',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.5',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'maintenance': None,
         'newly_discovered': None,
         'provision_state': 'deploying',
         'extra': {}
         })
    node_5 = node.Node(
        node.NodeManager(None),
        {'id': '5',
         'uuid': 'dd-55',
         'instance_uuid': 'dd',
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '5.5.5.5',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.6',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'error',
         'target_power_state': 'on',
         'provision_state': 'error',
         'maintenance': None,
         'newly_discovered': None,
         'extra': {}
         })
    node_6 = node.Node(
        node.NodeManager(None),
        {'id': '6',
         'uuid': 'ff-66',
         'instance_uuid': None,
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '5.5.5.5',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.6',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'maintenance': None,
         'newly_discovered': None,
         'provision_state': 'active',
         'extra': {}
         })
    node_7 = node.Node(
        node.NodeManager(None),
        {'id': '7',
         'uuid': 'gg-77',
         'instance_uuid': None,
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '7.7.7.7',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.7',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'off',
         'target_power_state': 'on',
         'maintenance': True,
         'newly_discovered': None,
         'provision_state': 'deploying',
         'extra': {}
         })
    node_8 = node.Node(
        node.NodeManager(None),
        {'id': '8',
         'uuid': 'hh-88',
         'instance_uuid': None,
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '8.8.8.8',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.8',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'maintenance': True,
         'newly_discovered': True,
         'provision_state': 'active',
         'extra': {}
         })
    node_9 = node.Node(
        node.NodeManager(None),
        {'id': '9',
         'uuid': 'ii-99',
         'instance_uuid': None,
         'driver': 'pxe_ipmitool',
         'driver_info': {
             'ipmi_address': '9.9.9.9',
             'ipmi_username': 'admin',
             'ipmi_password': 'password',
             'ip_address': '1.2.2.9',
             'deploy_kernel': 'deploy-kernel-uuid',
             'deploy_ramdisk': 'deploy-ramdisk-uuid',
         },
         'properties': {
             'cpus': '16',
             'memory_mb': '8192',
             'local_gb': '1000',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'maintenance': True,
         'newly_discovered': True,
         'provision_state': 'active',
         'extra': {}
         })
    TEST.ironicclient_nodes.add(node_1, node_2, node_3, node_4, node_5, node_6,
                                node_7, node_8, node_9)

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
