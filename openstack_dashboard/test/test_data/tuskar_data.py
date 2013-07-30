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

from openstack_dashboard.api.tuskar import (
    Flavor, FlavorTemplate, ResourceClass, Node,
    Rack, Capacity)
from collections import namedtuple

import openstack_dashboard.dashboards.infrastructure.models as dummymodels

from .utils import TestDataContainer


def data(TEST):
    FlavorStruct = namedtuple('FlavorStruct', 'id name\
        capacities')
    CapacityStruct = namedtuple('CapacityStruct', 'name value unit')
    TEST.tuskar_flavor_templates = TestDataContainer()
    flavor_template_1 = FlavorTemplate(FlavorStruct(
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
    flavor_template_2 = FlavorTemplate(FlavorStruct(
            id="2",
            name='large',
            capacities=[]))
    TEST.tuskar_flavor_templates.add(flavor_template_1, flavor_template_2)

    # Flavors
    TEST.tuskar_flavors = TestDataContainer()
    flavor_1 = Flavor(FlavorStruct(
            id="1",
            name='nano',
            capacities=[]))
    flavor_2 = Flavor(FlavorStruct(
            id="2",
            name='large',
            capacities=[]))
    TEST.tuskar_flavors.add(flavor_1, flavor_2)

    # Resource Classes
    TEST.tuskar_resource_classes = TestDataContainer()

    ResourceClassStruct = namedtuple('ResourceClassStruct', 'id service_type\
        name racks')
    resource_class_1 = ResourceClass(ResourceClassStruct(
        id="1",
        service_type="compute",
        racks=[{'id': 1}],
        name="rclass1"))

    resource_class_2 = ResourceClass(ResourceClassStruct(
        id="2",
        service_type="compute",
        racks=[],
        name="rclass2"))

    """
    # FIXME to make code below work, every @property has to have
    # setter defined in API model
    flavors = []
    all_flavors = []
    resources = []
    all_resources = []

    @resources.setter
    def resources(self, value):
        self._resources = value
    resource_class_1.resources = resources
    resource_class_2.resources = resources

    resource_class_1.all_resources = all_resources
    resource_class_2.all_resources = all_resources

    resource_class_1.flavors = flavors
    resource_class_2.flavors = flavors

    resource_class_1.all_flavors = all_flavors
    resource_class_2.all_flavors = all_flavors
    """

    TEST.tuskar_resource_classes.add(resource_class_1, resource_class_2)

    #Racks
    TEST.tuskar_racks = TestDataContainer()
    # FIXME: Struct is used to provide similar object-like behaviour
    # as is provided by tuskarclient
    RackStruct = namedtuple('RackStruct', 'id name nodes resource_class\
        location subnet state')
    rack_1 = Rack(RackStruct(
        id="1",
        name='rack1',
        location='location',
        subnet='192.168.1.0/24',
        state='provisioned',
        nodes=[{'id': '1'}, {'id': '2'}, {'id': '3'}, {'id': '4'}],
        resource_class={'id': '1'}))

    TEST.tuskar_racks.add(rack_1)

    # Nodes
    TEST.nodes = TestDataContainer()
    TEST.unracked_nodes = TestDataContainer()

    node_1 = Node(dummymodels.Node(id="1",
                                   name="node1",
                                   rack_id=1,
                                   mac_address="00-B0-D0-86-AB-F7",
                                   ip_address="192.168.191.11",
                                   status="active",
                                   usage="20"))
    node_2 = Node(dummymodels.Node(id="2",
                                   name="node2",
                                   rack_id=1,
                                   mac_address="00-B0-D0-86-AB-F8",
                                   ip_address="192.168.191.12",
                                   status="active",
                                   usage="20"))
    node_3 = Node(dummymodels.Node(id="3",
                                   name="node3",
                                   rack_id=1,
                                   mac_address="00-B0-D0-86-AB-F9",
                                   ip_address="192.168.191.13",
                                   status="active",
                                   usage="20"))
    node_4 = Node(dummymodels.Node(id="4",
                                   name="node4",
                                   rack_id=1,
                                   mac_address="00-B0-D0-86-AB-F0",
                                   ip_address="192.168.191.14",
                                   status="active",
                                   usage="20"))
    node_5 = Node(dummymodels.Node(id="5",
                                   name="node5",
                                   mac_address="00-B0-D0-86-AB-F1"))

    TEST.nodes.add(node_1, node_2, node_3, node_4)
    TEST.unracked_nodes.add(node_5)
