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

from collections import namedtuple

from tuskar_ui.api import Capacity
from tuskar_ui.api import Flavor
from tuskar_ui.api import FlavorTemplate
from tuskar_ui.api import Node
from tuskar_ui.api import Rack
from tuskar_ui.api import ResourceClass

from openstack_dashboard.test.test_data.utils import TestDataContainer

from novaclient.v1_1.contrib import baremetal
from tuskarclient.v1 import flavors
from tuskarclient.v1 import racks
from tuskarclient.v1 import resource_classes


def data(TEST):
    FlavorTemplateStruct = namedtuple('FlavorStruct', 'id name\
        capacities')
    CapacityStruct = namedtuple('CapacityStruct', 'name value unit')
    TEST.tuskar_flavor_templates = TestDataContainer()
    flavor_template_1 = FlavorTemplate(FlavorTemplateStruct(
            id="1",
            name='nano',
            capacities=[
              Capacity(CapacityStruct(
                name='cpu',
                unit='',
                value='1')),
              Capacity(CapacityStruct(
                name='memory',
                unit='MB',
                value='64')),
              Capacity(CapacityStruct(
                name='storage',
                unit='MB',
                value='128')),
              Capacity(CapacityStruct(
                name='ephemeral_disk',
                unit='GB',
                value='0')),
              Capacity(CapacityStruct(
                name='swap_disk',
                unit='GB',
                value='0'))]))
    flavor_template_2 = FlavorTemplate(FlavorTemplateStruct(
            id="2",
            name='large',
            capacities=[]))
    TEST.tuskar_flavor_templates.add(flavor_template_1, flavor_template_2)

    # Flavors
    TEST.tuskarclient_flavors = TestDataContainer()
    TEST.tuskar_flavors = TestDataContainer()
    flavor_1 = flavors.Flavor(flavors.FlavorManager(None),
                              {'id': '1',
                               'name': 'nano',
                               'max_vms': 100,
                               'capacities':
                                   [{"name": "cpu",
                                     "value": 64,
                                     "unit": "CPU"},
                                    {"name": "memory",
                                     "value": 1024,
                                     "unit": "MB"},
                                    {"name": "storage",
                                     "value": 1,
                                     "unit": "GB"},
                                    {"name": "ephemeral_disk",
                                     "value": 0,
                                     "unit": "GB"},
                                    {"name": "swap_disk",
                                     "value": 2,
                                     "unit": "GB"}]})
    flavor_2 = flavors.Flavor(flavors.FlavorManager(None),
                              {'id': '2',
                               'name': 'large',
                               'max_vms': 10,
                               'capacities': []})
    TEST.tuskarclient_flavors.add(flavor_1, flavor_2)
    TEST.tuskar_flavors.add(Flavor(flavor_1), Flavor(flavor_2))

    # Resource Classes
    TEST.tuskarclient_resource_classes = TestDataContainer()
    TEST.tuskar_resource_classes = TestDataContainer()
    resource_class_1 = resource_classes.ResourceClass(
        resource_classes.ResourceClassManager(None),
        {'id': '1',
         'service_type': 'compute',
         'racks': [{'id': 1}, {'id': 2}],
         'name': 'rclass1'})
    resource_class_2 = resource_classes.ResourceClass(
        resource_classes.ResourceClassManager(None),
        {'id': '2',
         'service_type': 'compute',
         'racks': [],
         'name': 'rclass2'})
    TEST.tuskarclient_resource_classes.add(resource_class_1, resource_class_2)
    TEST.tuskar_resource_classes.add(ResourceClass(resource_class_1),
                                     ResourceClass(resource_class_2))

    #Racks
    TEST.tuskarclient_racks = TestDataContainer()
    TEST.tuskar_racks = TestDataContainer()
    rack_1 = racks.Rack(racks.RackManager(None),
                        {'id': '1',
                         'name': 'rack1',
                         'location': 'location',
                         'subnet': '192.168.1.0/24',
                         'state': 'active',
                         'nodes':
                             [{'id': '1'},
                              {'id': '2'},
                              {'id': '3'},
                              {'id': '4'}],
                         'capacities':
                             [{"name": "total_cpu",
                               "value": "64",
                               "unit": "CPU"},
                              {"name": "total_memory",
                               "value": "1024",
                               "unit": "MB"}],
                         'resource_class': {'id': '1'}})
    rack_2 = racks.Rack(racks.RackManager(None),
                        {'id': '2',
                         'name': 'rack2',
                         'location': 'location',
                         'subnet': '192.168.1.0/25',
                         'state': 'provisioning',
                         'nodes': [],
                         'capacities':
                             [{"name": "total_cpu",
                               "value": "1",
                               "unit": "CPU"},
                              {"name": "total_memory",
                               "value": "4",
                               "unit": "MB"}],
                         'resource_class': {'id': '1'}})
    rack_3 = racks.Rack(racks.RackManager(None),
                        {'id': '3',
                         'name': 'rack3',
                         'location': 'location',
                         'subnet': '192.168.1.0/26',
                         'state': 'inactive',
                         'nodes': [],
                         'capacities':
                             [{"name": "total_cpu",
                               "value": "1",
                               "unit": "CPU"},
                              {"name": "total_memory",
                               "value": "2",
                               "unit": "MB"}],
                         'resource_class': None})
    TEST.tuskarclient_racks.add(rack_1, rack_2, rack_3)
    TEST.tuskar_racks.add(Rack(rack_1), Rack(rack_2), Rack(rack_3))

    # Nodes
    TEST.baremetalclient_nodes = TestDataContainer()
    TEST.baremetal_nodes = TestDataContainer()
    TEST.baremetalclient_unracked_nodes = TestDataContainer()
    TEST.baremetal_unracked_nodes = TestDataContainer()
    TEST.baremetalclient_nodes_all = TestDataContainer()
    TEST.baremetal_nodes_all = TestDataContainer()

    node_1 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '1',
         'name': 'node1',
         'prov_mac_address': '00-B0-D0-86-AB-F7'})
    node_2 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '2',
         'name': 'node2',
         'prov_mac_address': '00-B0-D0-86-AB-F8'})
    node_3 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '3',
         'name': 'node3',
         'prov_mac_address': '00-B0-D0-86-AB-F9'})
    node_4 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '4',
         'name': 'node4',
         'prov_mac_address': '00-B0-D0-86-AB-F0'})
    node_5 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'id': '5',
         'name': 'node5',
         'prov_mac_address': '00-B0-D0-86-AB-F1'})

    TEST.baremetalclient_nodes.add(node_1, node_2, node_3, node_4)
    TEST.baremetal_nodes.add(Node(node_1),
                             Node(node_2),
                             Node(node_3),
                             Node(node_4))
    TEST.baremetalclient_unracked_nodes.add(node_5)
    TEST.baremetal_unracked_nodes.add(Node(node_5))
    TEST.baremetalclient_nodes_all.add(node_1, node_2, node_3, node_4, node_5)
    TEST.baremetal_nodes_all.add(Node(node_1),
                             Node(node_2),
                             Node(node_3),
                             Node(node_4),
                             Node(node_5))
