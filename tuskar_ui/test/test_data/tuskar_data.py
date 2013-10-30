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

from tuskar_ui import api

from openstack_dashboard.test.test_data import utils as test_data_utils

from novaclient.v1_1.contrib import baremetal
from tuskarclient.v1 import flavors
from tuskarclient.v1 import nodes as tuskar_nodes
from tuskarclient.v1 import racks
from tuskarclient.v1 import resource_classes


def data(TEST):
    # Flavors
    TEST.tuskarclient_flavors = test_data_utils.TestDataContainer()
    TEST.tuskar_flavors = test_data_utils.TestDataContainer()
    flavor_1 = flavors.Flavor(flavors.FlavorManager(None),
                              {'id': '1',
                               'name': 'nano',
                               'max_vms': 100,
                               'capacities': [
                                   {"name": "cpu",
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
    TEST.tuskar_flavors.add(api.Flavor(flavor_1), api.Flavor(flavor_2))

    # Resource Classes
    TEST.tuskarclient_resource_classes = test_data_utils.TestDataContainer()
    TEST.tuskar_resource_classes = test_data_utils.TestDataContainer()
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
    TEST.tuskar_resource_classes.add(api.ResourceClass(resource_class_1),
                                     api.ResourceClass(resource_class_2))

    #Racks
    TEST.tuskarclient_racks = test_data_utils.TestDataContainer()
    TEST.tuskar_racks = test_data_utils.TestDataContainer()
    rack_1 = racks.Rack(racks.RackManager(None),
                        {'id': '1',
                         'name': 'rack1',
                         'location': 'location',
                         'subnet': '192.168.1.0/24',
                         'state': 'active',
                         'nodes': [
                             {'id': '1'},
                             {'id': '2'},
                             {'id': '3'},
                             {'id': '4'}],
                         'capacities': [
                             {"name": "total_cpu",
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
                         'capacities': [
                             {"name": "total_cpu",
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
                         'capacities': [
                             {"name": "total_cpu",
                              "value": "1",
                              "unit": "CPU"},
                             {"name": "total_memory",
                              "value": "2",
                              "unit": "MB"}],
                         })
    TEST.tuskarclient_racks.add(rack_1, rack_2, rack_3)
    TEST.tuskar_racks.add(api.Rack(rack_1), api.Rack(rack_2), api.Rack(rack_3))

    # Nodes
    TEST.tuskarclient_nodes = test_data_utils.TestDataContainer()
    TEST.tuskar_nodes = test_data_utils.TestDataContainer()

    tuskar_node_1 = tuskar_nodes.Node(
        tuskar_nodes.NodeManager(None),
        {'id': '1',
         'nova_baremetal_node_id': '11',
         'rack': {"id": "1"}})
    tuskar_node_2 = tuskar_nodes.Node(
        tuskar_nodes.NodeManager(None),
        {'id': '2',
         'nova_baremetal_node_id': '12',
         'rack': {"id": "1"}})
    tuskar_node_3 = tuskar_nodes.Node(
        tuskar_nodes.NodeManager(None),
        {'id': '3',
         'nova_baremetal_node_id': '13',
         'rack': {"id": "1"}})
    tuskar_node_4 = tuskar_nodes.Node(
        tuskar_nodes.NodeManager(None),
        {'id': '4',
         'nova_baremetal_node_id': '14',
         'rack': {"id": "1"}})

    TEST.tuskarclient_nodes.add(tuskar_node_1,
                                tuskar_node_2,
                                tuskar_node_3,
                                tuskar_node_4)
    TEST.tuskar_nodes.add(api.TuskarNode(tuskar_node_1),
                          api.TuskarNode(tuskar_node_2),
                          api.TuskarNode(tuskar_node_3),
                          api.TuskarNode(tuskar_node_4))

    TEST.baremetalclient_nodes = test_data_utils.TestDataContainer()
    TEST.baremetal_nodes = test_data_utils.TestDataContainer()
    TEST.baremetalclient_unracked_nodes = test_data_utils.TestDataContainer()
    TEST.baremetal_unracked_nodes = test_data_utils.TestDataContainer()
    TEST.baremetalclient_nodes_all = test_data_utils.TestDataContainer()
    TEST.baremetal_nodes_all = test_data_utils.TestDataContainer()

    baremetal_node_1 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'instance_uuid': 'uuid_11',
         'id': '11',
         'name': 'node1',
         'prov_mac_address': '00:B0:D0:86:AB:F7'})
    baremetal_node_2 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'instance_uuid': 'uuid_12',
         'id': '12',
         'name': 'node2',
         'prov_mac_address': '00:B0:D0:86:AB:F8'})
    baremetal_node_3 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'instance_uuid': 'uuid_13',
         'id': '13',
         'name': 'node3',
         'prov_mac_address': '00:B0:D0:86:AB:F9'})
    baremetal_node_4 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'instance_uuid': 'uuid_14',
         'id': '14',
         'name': 'node4',
         'prov_mac_address': '00:B0:D0:86:AB:F0'})
    baremetal_node_5 = baremetal.BareMetalNode(
        baremetal.BareMetalNodeManager(None),
        {'instance_uuid': 'uuid_15',
         'id': '15',
         'name': 'node5',
         'prov_mac_address': '00:B0:D0:86:AB:F1'})

    TEST.baremetalclient_nodes.add(baremetal_node_1, baremetal_node_2,
                                   baremetal_node_3, baremetal_node_4)
    TEST.baremetal_nodes.add(api.BaremetalNode(baremetal_node_1),
                             api.BaremetalNode(baremetal_node_2),
                             api.BaremetalNode(baremetal_node_3),
                             api.BaremetalNode(baremetal_node_4))
    TEST.baremetalclient_unracked_nodes.add(baremetal_node_5)
    TEST.baremetal_unracked_nodes.add(api.TuskarNode(baremetal_node_5))
    TEST.baremetalclient_nodes_all.add(baremetal_node_1, baremetal_node_2,
                                       baremetal_node_3, baremetal_node_4,
                                       baremetal_node_5)
    TEST.baremetal_nodes_all.add(api.BaremetalNode(baremetal_node_1),
                                 api.BaremetalNode(baremetal_node_2),
                                 api.BaremetalNode(baremetal_node_3),
                                 api.BaremetalNode(baremetal_node_4),
                                 api.BaremetalNode(baremetal_node_5))
