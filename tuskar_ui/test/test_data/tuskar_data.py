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

from glanceclient.v1 import images
from heatclient.v1 import events
from heatclient.v1 import resources
from heatclient.v1 import stacks
from ironicclient.v1 import node
from ironicclient.v1 import port
from novaclient.v1_1 import flavors
from novaclient.v1_1 import servers
from tuskarclient.v1 import overcloud_roles
from tuskarclient.v1 import overclouds


def data(TEST):

    # Stack
    TEST.heatclient_stacks = test_data_utils.TestDataContainer()
    stack_1 = stacks.Stack(
        stacks.StackManager(None),
        {'id': 'stack-id-1',
         'stack_name': 'overcloud',
         'stack_status': 'RUNNING',
         'outputs': [{
             'output_key': 'KeystoneURL',
             'output_value': 'http://192.0.2.23:5000/v2',
         }],
         'parameters': {
             'one': 'one',
             'two': 'two',
         }})
    TEST.heatclient_stacks.add(stack_1)

    # Events
    TEST.heatclient_events = test_data_utils.TestDataContainer()
    event_1 = events.Event(
        events.EventManager(None),
        {'id': 1,
         'stack_id': 'stack-id-1',
         'resource_name': 'Controller',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:26:15Z'})
    event_2 = events.Event(
        events.EventManager(None),
        {'id': 2,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute0',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:26:27Z'})
    event_3 = events.Event(
        events.EventManager(None),
        {'id': 3,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute1',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:26:44Z'})
    event_4 = events.Event(
        events.EventManager(None),
        {'id': 4,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute0',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:27:14Z'})
    event_5 = events.Event(
        events.EventManager(None),
        {'id': 5,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute2',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:27:31Z'})
    event_6 = events.Event(
        events.EventManager(None),
        {'id': 6,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute1',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:28:01Z'})
    event_7 = events.Event(
        events.EventManager(None),
        {'id': 7,
         'stack_id': 'stack-id-1',
         'resource_name': 'Controller',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:28:59Z'})
    event_8 = events.Event(
        events.EventManager(None),
        {'id': 8,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute2',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:29:11Z'})
    TEST.heatclient_events.add(event_1, event_2, event_3, event_4,
                               event_5, event_6, event_7, event_8)

    # Node
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
         },
         'properties': {
             'cpu': '8',
             'ram': '16',
             'local_disk': '10',
         },
         'power_state': 'on',

         # FIXME(lsmola) nova-baremetal test attrs, delete when Ironic is in
         "pm_address": None,
         "pm_user": None,
         "task_state": "active",
         "interfaces": [{"address": "52:54:00:90:38:01"},
                        {"address": "52:54:00:90:38:01"}],
         "cpus": 1,
         "memory_mb": 4096,
         "service_host": "undercloud",
         "local_gb": 20,
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
         },
         'properties': {
             'cpu': '16',
             'ram': '32',
             'local_disk': '100',
         },
         'power_state': 'on',

         # FIXME(lsmola) nova-baremetal test attrs, delete when Ironic is in
         "pm_address": None,
         "pm_user": None,
         "task_state": "active",
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         "cpus": 1,
         "memory_mb": 4096,
         "service_host": "undercloud",
         "local_gb": 20,
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
         },
         'properties': {
             'cpu': '32',
             'ram': '64',
             'local_disk': '1',
         },
         'power_state': 'rebooting',

         # FIXME(lsmola) nova-baremetal test attrs, delete when Ironic is in
         "pm_address": None,
         "pm_user": None,
         "task_state": "active",
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         "cpus": 1,
         "memory_mb": 4096,
         "service_host": "undercloud",
         "local_gb": 20,
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
         },
         'properties': {
             'cpu': '8',
             'ram': '16',
             'local_disk': '10',
         },
         'power_state': 'on',

         # FIXME(lsmola) nova-baremetal test attrs, delete when Ironic is in
         "pm_address": None,
         "pm_user": None,
         "task_state": "active",
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         "cpus": 1,
         "memory_mb": 4096,
         "service_host": "undercloud",
         "local_gb": 20,
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
         },
         'properties': {
             'cpu': '8',
             'ram': '16',
             'local_disk': '10',
         },
         'power_state': 'error',

         # FIXME(lsmola) nova-baremetal test attrs, delete when Ironic is in
         "pm_address": None,
         "pm_user": None,
         "task_state": "active",
         "interfaces": [{"address": "52:54:00:90:38:01"}],
         "cpus": 1,
         "memory_mb": 4096,
         "service_host": "undercloud",
         "local_gb": 20,
         })
    TEST.ironicclient_nodes.add(node_1, node_2, node_3, node_4, node_5)

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
        {'id': '1-resource-id',
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute0',
         'logical_resource_id': 'Compute0',
         'physical_resource_id': 'aa',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'AWS::EC2::Instance'})
    resource_2 = resources.Resource(
        resources.ResourceManager(None),
        {'id': '2-resource-id',
         'stack_id': 'stack-id-1',
         'resource_name': 'Controller',
         'logical_resource_id': 'Controller',
         'physical_resource_id': 'bb',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'AWS::EC2::Instance'})
    resource_3 = resources.Resource(
        resources.ResourceManager(None),
        {'id': '3-resource-id',
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute1',
         'logical_resource_id': 'Compute1',
         'physical_resource_id': 'cc',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'AWS::EC2::Instance'})
    resource_4 = resources.Resource(
        resources.ResourceManager(None),
        {'id': '4-resource-id',
         'stack_id': 'stack-id-4',
         'resource_name': 'Compute2',
         'logical_resource_id': 'Compute2',
         'physical_resource_id': 'dd',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'AWS::EC2::Instance'})
    TEST.heatclient_resources.add(resource_1,
                                  resource_2,
                                  resource_3,
                                  resource_4)

    # Server
    TEST.novaclient_servers = test_data_utils.TestDataContainer()
    s_1 = servers.Server(
        servers.ServerManager(None),
        {'id': 'aa',
         'name': 'Compute',
         'image': {'id': 1},
         'status': 'ACTIVE'})
    s_2 = servers.Server(
        servers.ServerManager(None),
        {'id': 'bb',
         'name': 'Controller',
         'image': {'id': 2},
         'status': 'ACTIVE'})
    s_3 = servers.Server(
        servers.ServerManager(None),
        {'id': 'cc',
         'name': 'Compute',
         'image': {'id': 1},
         'status': 'BUILD'})
    s_4 = servers.Server(
        servers.ServerManager(None),
        {'id': 'dd',
         'name': 'Compute',
         'image': {'id': 1},
         'status': 'ERROR'})
    TEST.novaclient_servers.add(s_1, s_2, s_3, s_4)

    # Overcloud
    TEST.tuskarclient_overclouds = test_data_utils.TestDataContainer()
    # TODO(Tzu-Mainn Chen): fix these to create Tuskar Overcloud objects
    # once the api supports it
    oc_1 = overclouds.Overcloud(
        overclouds.OvercloudManager(None),
        {'id': 1,
         'stack_id': 'stack-id-1',
         'name': 'overcloud',
         'description': 'overcloud',
         'attributes': {
             'AdminPassword': "unset"
         }})
    TEST.tuskarclient_overclouds.add(oc_1)

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

    # Image
    TEST.glanceclient_images = test_data_utils.TestDataContainer()
    image_1 = images.Image(
        images.ImageManager(None),
        {'id': '2',
         'name': 'overcloud-control'})
    image_2 = images.Image(
        images.ImageManager(None),
        {'id': '1',
         'name': 'overcloud-compute'})
    image_3 = images.Image(
        images.ImageManager(None),
        {'id': '3',
         'name': 'Object Storage Image'})
    image_4 = images.Image(
        images.ImageManager(None),
        {'id': '4',
         'name': 'Block Storage Image'})
    TEST.glanceclient_images.add(image_1, image_2, image_3, image_4)

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
