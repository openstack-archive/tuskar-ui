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
from novaclient.v1_1.contrib import baremetal
from openstack_dashboard.test.test_data import utils as test_data_utils


def data(TEST):

    # BareMetalNode
    TEST.baremetalclient_nodes = test_data_utils.TestDataContainer()
    bm_node_1 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '1',
         'uuid': 'd0ace338-a702-426a-b344-394ce861e070',
         'ipmi_address': '1.1.1.1',
         'ipmi_username': 'admin',
         'ipmi_password': 'password',
         'ip_address': '192.0.2.36',
         'instance_uuid': 'aa',
         "service_host": "undercloud",
         "cpus": 1,
         "memory_mb": 4096,
         "local_gb": 20,
         'task_state': 'active',
         "pm_address": '1.1.1.1',
         "pm_user": 'test1',
         "interfaces": [{"address": "52:54:00:90:38:01"},
                        {"address": "52:54:00:90:38:02"}],
         })
    bm_node_2 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '2',
         'uuid': 'bd70e5e7-52e6-40d6-b862-c7f7ea1f262e',
         'instance_uuid': 'bb',
         "service_host": "undercloud",
         "cpus": 1,
         "memory_mb": 4096,
         "local_gb": 20,
         'task_state': 'active',
         "pm_address": None,
         "pm_user": None,
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         })
    bm_node_3 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '3',
         'uuid': '74981-2cfa-4e15-be96-3f0ec5635115',
         'instance_uuid': 'cc',
         "service_host": "undercloud",
         "cpus": 1,
         "memory_mb": 4096,
         "local_gb": 20,
         'task_state': 'reboot',
         "pm_address": None,
         "pm_user": None,
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         })
    bm_node_4 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '4',
         'uuid': 'f5c1df48-dcbe-4eb5-bd44-9eef2cb9139a',
         'instance_uuid': 'cc',
         "service_host": "undercloud",
         "cpus": 1,
         "memory_mb": 4096,
         "local_gb": 20,
         'task_state': 'active',
         "pm_address": None,
         "pm_user": None,
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         })
    bm_node_5 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '5',
         'uuid': 'c8998d40-2ff6-4233-8535-b44a825b20c3',
         'instance_uuid': 'dd',
         "service_host": "undercloud",
         "cpus": 1,
         "memory_mb": 4096,
         "local_gb": 20,
         'task_state': 'error',
         "pm_address": None,
         "pm_user": None,
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         })
    bm_node_6 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '6',
         'uuid': 'cfd5a2cf-f21c-4044-a604-acb855478e44',
         'instance_uuid': None,
         "service_host": "undercloud",
         "cpus": 1,
         "memory_mb": 4096,
         "local_gb": 20,
         'task_state': None,
         "pm_address": None,
         "pm_user": None,
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         })
    TEST.baremetalclient_nodes.add(
        bm_node_1, bm_node_2, bm_node_3, bm_node_4, bm_node_5, bm_node_6)

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
             'ip_address': '1.2.2.2'
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'provision_state': 'active',
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
             'ip_address': '1.2.2.3'
         },
         'properties': {
             'cpus': '16',
             'memory_mb': '4096',
             'local_gb': '100',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'provision_state': 'active',
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
             'ip_address': '1.2.2.4'
         },
         'properties': {
             'cpus': '32',
             'memory_mb': '8192',
             'local_gb': '1',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'rebooting',
         'target_power_state': 'on',
         'provision_state': 'active',
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
             'ip_address': '1.2.2.5'
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'provision_state': 'active',
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
             'ip_address': '1.2.2.6'
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
         'provision_state': 'deploying',
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
             'ip_address': '1.2.2.6'
         },
         'properties': {
             'cpus': '8',
             'memory_mb': '4096',
             'local_gb': '10',
             'cpu_arch': 'x86_64',
         },
         'power_state': 'on',
         'target_power_state': 'on',
         'provision_state': 'active',
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
             'ip_address': '1.2.2.7'
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
             'ip_address': '1.2.2.8'
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
             'ip_address': '1.2.2.9'
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
