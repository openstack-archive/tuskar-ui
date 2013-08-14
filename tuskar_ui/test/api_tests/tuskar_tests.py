# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
#
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

from __future__ import absolute_import

from novaclient.v1_1.contrib import baremetal

from tuskar_ui.api import Capacity
from tuskar_ui.api import Flavor
from tuskar_ui.api import FlavorTemplate
from tuskar_ui.api import Node
from tuskar_ui.api import Rack
from tuskar_ui.api import ResourceClass
from tuskar_ui.test import helpers as test


class TuskarApiTests(test.APITestCase):

    def test_node_get(self):
        node = self.baremetalclient_nodes.first()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        baremetal.BareMetalNodeManager.get(node.id).AndReturn(node)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).AndReturn([])
        self.mox.ReplayAll()

        ret_val = Node.get(self.request, node.id)
        self.assertIsInstance(ret_val, Node)

    def test_node_create(self):
        node = self.baremetalclient_nodes.first()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'create')
        baremetal.BareMetalNodeManager.create('node',
                                              1,
                                              1024,
                                              10,
                                              'aa:bb:cc:dd:ee',
                                              '0.0.0.0',
                                              'user',
                                              'password',
                                              0).AndReturn(node)
        self.mox.ReplayAll()

        ret_val = Node.create(self.request,
                              name='node',
                              cpus=1,
                              memory_mb=1024,
                              local_gb=10,
                              prov_mac_address='aa:bb:cc:dd:ee',
                              pm_address='0.0.0.0',
                              pm_user='user',
                              pm_password='password',
                              terminal_port=0)
        self.assertIsInstance(ret_val, Node)

    def test_node_list(self):
        nodes = self.baremetalclient_nodes_all.list()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'list')
        baremetal.BareMetalNodeManager.list().AndReturn(nodes)
        self.mox.ReplayAll()

        ret_val = Node.list(self.request)
        for node in ret_val:
            self.assertIsInstance(node, Node)

    def test_node_list_unracked(self):
        nodes = self.baremetalclient_nodes.list()
        all_nodes = self.baremetalclient_nodes_all.list()
        racks = self.tuskarclient_racks.list()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'list')
        baremetal.BareMetalNodeManager.list().AndReturn(all_nodes)

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.list().MultipleTimes().AndReturn(racks)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).\
                MultipleTimes().AndReturn(n)
        self.mox.ReplayAll()

        ret_val = Node.list_unracked(self.request)
        for node in ret_val:
            self.assertIsInstance(node, Node)
        self.assertEquals(1, len(ret_val))

    def test_node_flavors(self):
        node = self.baremetal_nodes.first()
        nodes = self.baremetalclient_nodes.list()
        racks = self.tuskarclient_racks.list()
        rc = self.tuskarclient_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.list().AndReturn(racks)
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).AndReturn(n)
        self.mox.ReplayAll()

        node.request = self.request
        ret_val = node.list_flavors
        for flavor in ret_val:
            self.assertIsInstance(flavor, Flavor)
        self.assertEquals(2, len(ret_val))

    def test_node_rack(self):
        node = self.baremetal_nodes.first()
        nodes = self.baremetalclient_nodes.list()
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.list().AndReturn(racks)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).AndReturn(n)
        self.mox.ReplayAll()

        node.request = self.request
        rack = node.rack
        self.assertIsInstance(rack, Rack)
        self.assertEquals('1', rack.id)

    def test_node_running_instances(self):
        node = self.baremetal_nodes.first()

        self.assertEquals(4, node.running_instances)

    def test_node_remaining_capacity(self):
        node = self.baremetal_nodes.first()

        self.assertEquals(96, node.remaining_capacity)

    def test_node_is_provisioned(self):
        node = self.baremetal_nodes.first()
        nodes = self.baremetalclient_nodes.list()
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.list().AndReturn(racks)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).AndReturn(n)
        self.mox.ReplayAll()

        node.request = self.request
        node.status = 'provisioned'
        self.assertTrue(node.is_provisioned)

    def test_resource_class_list(self):
        rcs = self.tuskarclient_resource_classes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.list().AndReturn(rcs)
        self.mox.ReplayAll()

        ret_val = ResourceClass.list(self.request)
        for rc in ret_val:
            self.assertIsInstance(rc, ResourceClass)

    def test_resource_class_get(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        self.mox.ReplayAll()

        ret_val = ResourceClass.get(self.request, rc.id)
        self.assertIsInstance(ret_val, ResourceClass)

    def test_resource_class_create(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.create(name='rclass1',
                                             service_type='compute',
                                             flavors=[]).AndReturn(rc)
        self.mox.ReplayAll()

        ret_val = ResourceClass.create(self.request,
                                                  name='rclass1',
                                                  service_type='compute',
                                                  flavors=[])
        self.assertIsInstance(ret_val, ResourceClass)

    def test_resource_class_update(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.update(
            rc.id,
            name='rclass1',
            service_type='compute',
            flavors=[]).AndReturn(rc)
        tuskarclient.flavors.list(rc.id).AndReturn([])
        self.mox.ReplayAll()

        ret_val = ResourceClass.update(self.request, rc.id,
                                                  name='rclass1',
                                                  service_type='compute',
                                                  flavors=[])
        self.assertIsInstance(ret_val, ResourceClass)

    def test_resource_class_delete(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.delete(rc.id)
        self.mox.ReplayAll()

        ResourceClass.delete(self.request, rc.id)

    def test_resource_class_deletable(self):
        rc = self.tuskar_resource_classes.first()

        self.assertFalse(rc.deletable)

    def test_resource_class_racks(self):
        rc = self.tuskar_resource_classes.first()
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get('1').AndReturn(racks[0])
        tuskarclient.racks.get('2').AndReturn(racks[1])
        self.mox.ReplayAll()

        for rack in rc.list_racks:
            self.assertIsInstance(rack, Rack)
        self.assertEquals(2, rc.racks_count)

    def test_resource_class_all_racks(self):
        rc = self.tuskar_resource_classes.first()
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.list().AndReturn(racks)
        self.mox.ReplayAll()

        all_racks = rc.all_racks
        for rack in all_racks:
            self.assertIsInstance(rack, Rack)
        self.assertEquals(3, len(all_racks))

    def test_resource_class_racks_set(self):
        rc = self.tuskar_resource_classes.first()
        racks = self.tuskarclient_racks.list()
        rack_ids = [rack.id for rack in racks]
        rack_data = [{'id': rack_id} for rack_id in rack_ids]

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.update(rc.id,
                                             racks=[])
        tuskarclient.resource_classes.update(rc.id,
                                             racks=rack_data)
        self.mox.ReplayAll()

        rc.set_racks(self.request, rack_ids)

    def test_resource_class_nodes(self):
        rc = self.tuskar_resource_classes.first()
        racks = self.tuskarclient_racks.list()
        nodes = self.baremetalclient_nodes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get('1').AndReturn(racks[0])
        tuskarclient.racks.get('2').AndReturn(racks[1])

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).AndReturn(n)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])
        self.mox.ReplayAll()

        rc.request = self.request
        for node in rc.nodes:
            self.assertIsInstance(node, Node)
        self.assertEquals(4, rc.nodes_count)

    def test_resource_class_flavors(self):
        rc = self.tuskar_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        for f in rc.list_flavors:
            self.assertIsInstance(f, Flavor)
        self.assertEquals(2, len(rc.flavors_ids))

    def test_resource_class_capacities(self):
        rc = self.tuskar_resource_classes.first()
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get('1').AndReturn(racks[0])
        tuskarclient.racks.get('2').AndReturn(racks[1])
        self.mox.ReplayAll()

        for capacity in rc.capacities:
            self.assertIsInstance(capacity, Capacity)
        self.assertEquals(2, len(rc.capacities))

    def test_resource_class_total_instances(self):
        rc = self.tuskar_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        self.assertEquals(15, rc.total_instances)

    def test_resource_class_remaining_capacity(self):
        rc = self.tuskar_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        self.assertEquals(85, rc.remaining_capacity)

    def test_resource_class_vm_capacity(self):
        rc = self.tuskar_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        vm_capacity = rc.vm_capacity
        self.assertIsInstance(vm_capacity, Capacity)
        self.assertEquals(200, vm_capacity.value)

    def test_resource_class_has_provisioned_rack(self):
        rc1 = self.tuskar_resource_classes.list()[0]
        rc2 = self.tuskar_resource_classes.list()[1]
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get('1').AndReturn(racks[0])
        tuskarclient.racks.get('2').AndReturn(racks[1])
        self.mox.ReplayAll()

        self.assertTrue(rc1.has_provisioned_rack)
        self.assertFalse(rc2.has_provisioned_rack)

    def test_resource_class_aggregated_alerts(self):
        rc = self.tuskar_resource_classes.list()[0]
        rc.request = self.request

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        racks = self.tuskarclient_racks.list()
        tuskarclient.racks.get('1').AndReturn(racks[0])
        tuskarclient.racks.get('2').AndReturn(racks[1])

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        nodes = self.baremetalclient_nodes.list()
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).AndReturn(n)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])

        self.mox.ReplayAll()

        for rack in rc.aggregated_alerts:
            self.assertIsInstance(rack, Rack)
        self.assertEquals(1, len(rc.aggregated_alerts))

    def test_rack_list(self):
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.list().AndReturn(racks)
        self.mox.ReplayAll()

        ret_val = Rack.list(self.request)
        for rack in ret_val:
            self.assertIsInstance(rack, Rack)

    def test_rack_get(self):
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get(rack.id).AndReturn(rack)
        self.mox.ReplayAll()

        ret_val = Rack.get(self.request, rack.id)
        self.assertIsInstance(ret_val, Rack)

    def test_rack_create(self):
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.create(name='rack1',
                                  location='location',
                                  subnet='192.168.1.0/24',
                                  nodes=[],
                                  resource_class={'id': 1},
                                  slots=0).AndReturn(rack)
        self.mox.ReplayAll()

        ret_val = Rack.create(request=self.request,
                              name='rack1',
                              resource_class_id=1,
                              location='location',
                              subnet='192.168.1.0/24')
        self.assertIsInstance(ret_val, Rack)

    def test_rack_update(self):
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.update(rack.id,
                                  name='rack1').AndReturn(rack)
        self.mox.ReplayAll()

        ret_val = Rack.update(self.request,
                              rack.id,
                              {'name': 'rack1'})
        self.assertIsInstance(ret_val, Rack)

    def test_rack_delete(self):
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.delete(rack.id)
        self.mox.ReplayAll()

        Rack.delete(self.request, rack.id)

    def test_rack_nodes(self):
        rack = self.tuskar_racks.first()
        nodes = self.baremetalclient_nodes.list()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).AndReturn(n)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])
        self.mox.ReplayAll()

        rack.request = self.request
        for node in rack.list_nodes:
            self.assertIsInstance(node, Node)
        self.assertEquals(4, len(rack.node_ids))
        self.assertEquals(4, rack.nodes_count)

    def test_rack_resource_class(self):
        rc = self.tuskarclient_resource_classes.first()
        rack = self.tuskar_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        self.mox.ReplayAll()

        self.assertIsInstance(rack.get_resource_class, ResourceClass)
        self.assertEquals(rack.resource_class_id, '1')

    def test_rack_capacities(self):
        rack = self.tuskar_racks.first()

        for capacity in rack.list_capacities:
            self.assertIsInstance(capacity, Capacity)
        self.assertEquals(2, len(rack.capacities))

    def test_rack_vm_capacity(self):
        rack = self.tuskar_racks.first()
        rc = self.tuskarclient_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        vm_capacity = rack.vm_capacity
        self.assertIsInstance(vm_capacity, Capacity)
        self.assertEquals(100, vm_capacity.value)

    def test_rack_flavors(self):
        rack = self.tuskar_racks.first()
        rc = self.tuskarclient_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        rack_flavors = rack.list_flavors
        for f in rack_flavors:
            self.assertIsInstance(f, Flavor)
        self.assertEquals(2, len(rack_flavors))

    def test_rack_total_instances(self):
        rack = self.tuskar_racks.first()
        rc = self.tuskarclient_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        self.assertEquals(6, rack.total_instances)

    def test_rack_remaining_capacity(self):
        rack = self.tuskar_racks.first()
        rc = self.tuskarclient_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        self.assertEquals(94, rack.remaining_capacity)

    def test_rack_is_provisioned(self):
        rack1 = self.tuskar_racks.list()[0]
        rack2 = self.tuskar_racks.list()[1]

        self.assertTrue(rack1.is_provisioned)
        self.assertFalse(rack2.is_provisioned)

    def test_rack_is_provisioning(self):
        rack1 = self.tuskar_racks.list()[0]
        rack2 = self.tuskar_racks.list()[1]

        self.assertFalse(rack1.is_provisioning)
        self.assertTrue(rack2.is_provisioning)

    def test_rack_provision(self):
        rack = self.tuskar_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.data_centers = self.mox.CreateMockAnything()
        tuskarclient.data_centers.provision_all()
        self.mox.ReplayAll()

        Rack.provision(self.request, rack.id)

    def test_rack_aggregated_alerts(self):
        rack = self.tuskar_racks.first()
        rack.request = self.request

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        nodes = self.baremetalclient_nodes.list()
        for n in nodes:
            baremetal.BareMetalNodeManager.get(n.id).AndReturn(n)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).MultipleTimes().AndReturn([])

        self.mox.ReplayAll()

        for node in rack.aggregated_alerts:
            self.assertIsInstance(node, Node)
        self.assertEquals(1, len(rack.aggregated_alerts))

    def test_flavor_template_list(self):
        templates = FlavorTemplate.list(self.request)
        self.assertEquals(7, len(templates))
        for t in templates:
            self.assertIsInstance(t, FlavorTemplate)

    def test_flavor_template_get(self):
        test_template = self.tuskar_flavor_templates.first()
        template = FlavorTemplate.get(self.request,
                                                 test_template.id)
        self.assertIsInstance(template, FlavorTemplate)
        self.assertEquals(template.name, test_template.name)

    def test_flavor_create(self):
        flavor = self.tuskarclient_flavors.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.create(1,
                                   name='nano',
                                   max_vms=100,
                                   capacities=[]).AndReturn(flavor)
        self.mox.ReplayAll()

        ret_val = Flavor.create(self.request,
                              resource_class_id=1,
                              name='nano',
                              max_vms=100,
                              capacities=[])
        self.assertIsInstance(ret_val, Flavor)

    def test_flavor_delete(self):
        rc = self.tuskarclient_resource_classes.first()
        flavor = self.tuskarclient_flavors.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.delete(rc.id, flavor.id)
        self.mox.ReplayAll()

        Flavor.delete(self.request, resource_class_id=rc.id,
                                    flavor_id=flavor.id)

    def test_flavor_cpu(self):
        flavor = self.tuskar_flavors.first()

        cpu = flavor.cpu
        self.assertIsInstance(cpu, Capacity)
        self.assertEquals(64, cpu.value)

    def test_flavor_memory(self):
        flavor = self.tuskar_flavors.first()

        memory = flavor.memory
        self.assertIsInstance(memory, Capacity)
        self.assertEquals(1024, memory.value)

    def test_flavor_storage(self):
        flavor = self.tuskar_flavors.first()

        storage = flavor.storage
        self.assertIsInstance(storage, Capacity)
        self.assertEquals(1, storage.value)

    def test_flavor_ephemeral_disk(self):
        flavor = self.tuskar_flavors.first()

        ephemeral_disk = flavor.ephemeral_disk
        self.assertIsInstance(ephemeral_disk, Capacity)
        self.assertEquals(0, ephemeral_disk.value)

    def test_flavor_swap_disk(self):
        flavor = self.tuskar_flavors.first()

        swap_disk = flavor.swap_disk
        self.assertIsInstance(swap_disk, Capacity)
        self.assertEquals(2, swap_disk.value)
