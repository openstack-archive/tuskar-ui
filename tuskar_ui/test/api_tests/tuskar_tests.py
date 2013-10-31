# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class TuskarApiTests(test.APITestCase):

    def test_baremetal_node_create(self):
        baremetal_node = self.baremetalclient_nodes.first()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'create')
        baremetal.BareMetalNodeManager.create(
            'node',
            1,
            1024,
            10,
            'aa:bb:cc:dd:ee:ff',
            '0.0.0.0',
            'user',
            'password',
            0).AndReturn(baremetal_node)
        self.mox.ReplayAll()

        ret_val = api.BaremetalNode.create(
            self.request,
            service_host='node',
            cpus=1,
            memory_mb=1024,
            local_gb=10,
            prov_mac_address='aa:bb:cc:dd:ee:ff',
            pm_address='0.0.0.0',
            pm_user='user',
            pm_password='password',
            terminal_port=0)
        self.assertIsInstance(ret_val, api.BaremetalNode)

    def test_baremetal_node_create_with_empty_pm(self):
        """Make sure that when pm_address, pm_user and terminal_port are not
        provided (empty), their values are set to None, as this is required by
        the baremetal VM.
        """
        baremetal_node = self.baremetalclient_nodes.first()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'create')
        baremetal.BareMetalNodeManager.create(
            'node', 1, 1024, 10,
            'AA:BB:CC:DD:EE:FF',
            None, None, '', None).AndReturn(baremetal_node)
        self.mox.ReplayAll()

        ret_val = api.BaremetalNode.create(
            self.request, service_host='node', cpus=1,
            memory_mb=1024, local_gb=10, prov_mac_address='AA:BB:CC:DD:EE:FF',
            pm_address='', pm_user='', pm_password='', terminal_port='')
        self.assertIsInstance(ret_val, api.BaremetalNode)

    def test_baremetal_node_get(self):
        baremetal_node = self.baremetalclient_nodes.first()
        server = self.servers.first()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        baremetal.BareMetalNodeManager.get(
            baremetal_node.id).AndReturn(baremetal_node)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.get(baremetal_node.instance_uuid).AndReturn(server)

        self.mox.ReplayAll()

        ret_val = api.BaremetalNode.get(self.request, baremetal_node.id)
        self.assertIsInstance(ret_val, api.BaremetalNode)

    def test_baremetal_node_list(self):
        baremetal_nodes = self.baremetalclient_nodes_all.list()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'list')
        baremetal.BareMetalNodeManager.list().AndReturn(baremetal_nodes)
        self.mox.ReplayAll()

        ret_val = api.BaremetalNode.list(self.request)
        for baremetal_node in ret_val:
            self.assertIsInstance(baremetal_node, api.BaremetalNode)

    def test_baremetal_node_list_unracked(self):
        tuskarclient_nodes = self.tuskarclient_nodes.list()
        baremetal_nodes = self.baremetalclient_nodes_all.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.nodes = self.mox.CreateMockAnything()
        tuskarclient.nodes.list().AndReturn(tuskarclient_nodes)

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'list')
        baremetal.BareMetalNodeManager.list().AndReturn(baremetal_nodes)

        self.mox.ReplayAll()

        ret_val = api.BaremetalNode.list_unracked(self.request)
        for baremetal_node in ret_val:
            self.assertIsInstance(baremetal_node, api.BaremetalNode)
        self.assertEquals(1, len(ret_val))

    def test_baremetal_node_running_instances(self):
        baremetal_node = self.baremetal_nodes.first()

        self.assertEquals(4, baremetal_node.running_instances)

    def test_baremetal_node_remaining_capacity(self):
        baremetal_node = self.baremetal_nodes.first()

        self.assertEquals(96, baremetal_node.remaining_capacity)

    def test_node_get(self):
        tuskar_node = self.tuskarclient_nodes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.nodes = self.mox.CreateMockAnything()
        tuskarclient.nodes.get(tuskar_node.id).AndReturn(tuskar_node)
        self.mox.ReplayAll()

        ret_val = api.TuskarNode.get(self.request, tuskar_node.id)
        self.assertIsInstance(ret_val, api.TuskarNode)

    def test_node_list(self):
        tuskarclient_nodes = self.tuskarclient_nodes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.nodes = self.mox.CreateMockAnything()
        tuskarclient.nodes.list().AndReturn(tuskarclient_nodes)
        self.mox.ReplayAll()

        ret_val = api.TuskarNode.list(self.request)
        for tuskar_node in ret_val:
            self.assertIsInstance(tuskar_node, api.TuskarNode)

    def test_node_remove_from_rack(self):
        tuskar_nodes = self.tuskar_nodes.list()
        tuskar_node = tuskar_nodes[0]
        rack = self.tuskar_racks.first()

        self.mox.StubOutWithMock(api.Rack, 'get')
        self.mox.StubOutWithMock(api.Rack, 'update')
        self.mox.StubOutWithMock(api.Rack, 'list_tuskar_nodes')

        api.Rack.get(self.request, rack.id).AndReturn(rack)
        api.Rack.list_tuskar_nodes = tuskar_nodes
        api.Rack.update(self.request, rack.id, {
            'baremetal_nodes': [{'id': t_node.nova_baremetal_node_id}
                                for t_node in tuskar_nodes
                                if t_node.id != tuskar_node.id],
        }).AndReturn(rack)
        self.mox.ReplayAll()

        tuskar_node.request = self.request
        rack.request = self.request
        tuskar_node.remove_from_rack(self.request)

    def test_node_rack(self):
        tuskar_node = self.tuskar_nodes.first()
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get(rack.id).AndReturn(rack)
        self.mox.ReplayAll()

        tuskar_node.request = self.request
        self.assertIsInstance(tuskar_node.rack, api.Rack)
        self.assertEquals('1', tuskar_node.rack_id)

    def test_node_nova_baremetal_node(self):
        tuskar_node = self.tuskar_nodes.first()
        bm_node = self.baremetalclient_nodes.first()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        baremetal.BareMetalNodeManager.get(
            tuskar_node.nova_baremetal_node_id).AndReturn(bm_node)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).AndReturn([])
        self.mox.ReplayAll()

        tuskar_node.request = self.request
        baremetal_node = tuskar_node.nova_baremetal_node
        self.assertIsInstance(baremetal_node, api.BaremetalNode)
        self.assertEquals('11', baremetal_node.id)

    def test_node_flavors(self):
        tuskar_node = self.tuskar_nodes.first()
        rack = self.tuskarclient_racks.first()
        rc = self.tuskarclient_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get(rack.id).AndReturn(rack)
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        tuskar_node.request = self.request
        ret_val = tuskar_node.list_flavors
        for flavor in ret_val:
            self.assertIsInstance(flavor, api.Flavor)
        self.assertEquals(2, len(ret_val))

    def test_node_is_provisioned(self):
        tuskar_node = self.tuskar_nodes.first()
        tuskar_node.request = self.request
        bm_node = self.baremetalclient_nodes.first()

        self.mox.StubOutWithMock(baremetal.BareMetalNodeManager, 'get')
        baremetal.BareMetalNodeManager.get(
            tuskar_node.nova_baremetal_node_id).AndReturn(bm_node)

        novaclient = self.stub_novaclient()
        novaclient.servers = self.mox.CreateMockAnything()
        novaclient.servers.list(True,
                                {'all_tenants': True,
                                 'limit': 21}).AndReturn([])
        self.mox.ReplayAll()

        self.assertFalse(tuskar_node.is_provisioned)

    def test_node_alerts(self):
        tuskar_node = self.tuskar_nodes.first()

        self.assertEquals([], tuskar_node.alerts)

    def test_resource_class_list(self):
        rcs = self.tuskarclient_resource_classes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.list().AndReturn(rcs)
        self.mox.ReplayAll()

        ret_val = api.ResourceClass.list(self.request)
        for rc in ret_val:
            self.assertIsInstance(rc, api.ResourceClass)

    def test_resource_class_get(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        self.mox.ReplayAll()

        ret_val = api.ResourceClass.get(self.request, rc.id)
        self.assertIsInstance(ret_val, api.ResourceClass)

    def test_resource_class_create(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.create(name='rclass1',
                                             service_type='compute',
                                             image_id=None,
                                             flavors=[]).AndReturn(rc)
        self.mox.ReplayAll()

        ret_val = api.ResourceClass.create(self.request,
                                           name='rclass1',
                                           service_type='compute',
                                           image_id=None,
                                           flavors=[])
        self.assertIsInstance(ret_val, api.ResourceClass)

    def test_resource_class_update(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.update(rc.id,
                                             name='rclass1',
                                             service_type='compute',
                                             image_id=None,
                                             flavors=[]).AndReturn(rc)
        tuskarclient.flavors.list(rc.id).AndReturn([])
        self.mox.ReplayAll()

        ret_val = api.ResourceClass.update(self.request, rc.id,
                                           name='rclass1',
                                           service_type='compute',
                                           image_id=None,
                                           flavors=[])
        self.assertIsInstance(ret_val, api.ResourceClass)

    def test_resource_class_delete(self):
        rc = self.tuskarclient_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.delete(rc.id)
        self.mox.ReplayAll()

        api.ResourceClass.delete(self.request, rc.id)

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
            self.assertIsInstance(rack, api.Rack)
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
            self.assertIsInstance(rack, api.Rack)
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
        tuskar_nodes = self.tuskarclient_nodes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.nodes = self.mox.CreateMockAnything()
        tuskarclient.nodes.list().AndReturn(tuskar_nodes)
        self.mox.ReplayAll()

        rc.request = self.request
        for tuskar_node in rc.tuskar_nodes:
            self.assertIsInstance(tuskar_node, api.TuskarNode)
        self.assertEquals(4, rc.nodes_count)

    def test_resource_class_flavors(self):
        rc = self.tuskar_resource_classes.first()
        flavors = self.tuskarclient_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        for f in rc.list_flavors:
            self.assertIsInstance(f, api.Flavor)
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
            self.assertIsInstance(capacity, api.Capacity)
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
        self.assertIsInstance(vm_capacity, api.Capacity)
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
        tuskar_nodes = self.tuskarclient_nodes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        racks = self.tuskarclient_racks.list()
        tuskarclient.racks.get('1').AndReturn(racks[0])
        tuskarclient.racks.get('2').AndReturn(racks[1])

        tuskarclient.nodes = self.mox.CreateMockAnything()
        for tuskar_node in tuskar_nodes:
            tuskarclient.nodes.get(tuskar_node.id).AndReturn(tuskar_node)

        self.mox.ReplayAll()

        for rack in rc.aggregated_alerts:
            self.assertIsInstance(rack, api.Rack)
        self.assertEquals(0, len(rc.aggregated_alerts))

    def test_rack_list(self):
        racks = self.tuskarclient_racks.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.list().AndReturn(racks)
        self.mox.ReplayAll()

        ret_val = api.Rack.list(self.request)
        for rack in ret_val:
            self.assertIsInstance(rack, api.Rack)

    def test_rack_get(self):
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get(rack.id).AndReturn(rack)
        self.mox.ReplayAll()

        ret_val = api.Rack.get(self.request, rack.id)
        self.assertIsInstance(ret_val, api.Rack)

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

        ret_val = api.Rack.create(request=self.request,
                                  name='rack1',
                                  resource_class_id=1,
                                  location='location',
                                  subnet='192.168.1.0/24')
        self.assertIsInstance(ret_val, api.Rack)

    def test_rack_update(self):
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.update(rack.id,
                                  name='rack1').AndReturn(rack)
        self.mox.ReplayAll()

        ret_val = api.Rack.update(self.request,
                                  rack.id,
                                  {'name': 'rack1'})
        self.assertIsInstance(ret_val, api.Rack)

    def test_rack_delete(self):
        rack = self.tuskarclient_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.delete(rack.id)
        self.mox.ReplayAll()

        api.Rack.delete(self.request, rack.id)

    def test_rack_nodes(self):
        rack = self.tuskar_racks.first()
        tuskar_nodes = self.tuskarclient_nodes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.nodes = self.mox.CreateMockAnything()
        for tuskar_node in tuskar_nodes:
            tuskarclient.nodes.get(tuskar_node.id).AndReturn(tuskar_node)
        self.mox.ReplayAll()

        rack.request = self.request
        for tuskar_node in rack.list_tuskar_nodes:
            self.assertIsInstance(tuskar_node, api.TuskarNode)
        self.assertEquals(4, len(rack.tuskar_node_ids))
        self.assertEquals(4, rack.nodes_count)

    def test_rack_resource_class(self):
        rc = self.tuskarclient_resource_classes.first()
        rack = self.tuskar_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        self.mox.ReplayAll()

        self.assertIsInstance(rack.resource_class, api.ResourceClass)
        self.assertEquals(rack.resource_class_id, '1')

    def test_rack_capacities(self):
        rack = self.tuskar_racks.first()

        for capacity in rack.list_capacities:
            self.assertIsInstance(capacity, api.Capacity)
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
        self.assertIsInstance(vm_capacity, api.Capacity)
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
            self.assertIsInstance(f, api.Flavor)
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
        tuskarclient = self.stub_tuskarclient()
        tuskarclient.data_centers = self.mox.CreateMockAnything()
        tuskarclient.data_centers.provision_all()
        self.mox.ReplayAll()

        api.Rack.provision_all(self.request)

    def test_rack_aggregated_alerts(self):
        rack = self.tuskar_racks.first()
        rack.request = self.request
        tuskar_nodes = self.tuskarclient_nodes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.nodes = self.mox.CreateMockAnything()
        for tuskar_node in tuskar_nodes:
            tuskarclient.nodes.get(tuskar_node.id).AndReturn(tuskar_node)
        self.mox.ReplayAll()

        for tuskar_node in rack.aggregated_alerts:
            self.assertIsInstance(tuskar_node, api.TuskarNode)
        self.assertEquals(0, len(rack.aggregated_alerts))

    def test_flavor_create(self):
        flavor = self.tuskarclient_flavors.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.create(1,
                                    name='nano',
                                    max_vms=100,
                                    capacities=[]).AndReturn(flavor)
        self.mox.ReplayAll()

        ret_val = api.Flavor.create(self.request,
                                    resource_class_id=1,
                                    name='nano',
                                    max_vms=100,
                                    capacities=[])
        self.assertIsInstance(ret_val, api.Flavor)

    def test_flavor_delete(self):
        rc = self.tuskarclient_resource_classes.first()
        flavor = self.tuskarclient_flavors.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.delete(rc.id, flavor.id)
        self.mox.ReplayAll()

        api.Flavor.delete(self.request,
                          resource_class_id=rc.id,
                          flavor_id=flavor.id)

    def test_flavor_cpu(self):
        flavor = self.tuskar_flavors.first()

        cpu = flavor.cpu
        self.assertIsInstance(cpu, api.Capacity)
        self.assertEquals(64, cpu.value)

    def test_flavor_memory(self):
        flavor = self.tuskar_flavors.first()

        memory = flavor.memory
        self.assertIsInstance(memory, api.Capacity)
        self.assertEquals(1024, memory.value)

    def test_flavor_storage(self):
        flavor = self.tuskar_flavors.first()

        storage = flavor.storage
        self.assertIsInstance(storage, api.Capacity)
        self.assertEquals(1, storage.value)

    def test_flavor_ephemeral_disk(self):
        flavor = self.tuskar_flavors.first()

        ephemeral_disk = flavor.ephemeral_disk
        self.assertIsInstance(ephemeral_disk, api.Capacity)
        self.assertEquals(0, ephemeral_disk.value)

    def test_flavor_swap_disk(self):
        flavor = self.tuskar_flavors.first()

        swap_disk = flavor.swap_disk
        self.assertIsInstance(swap_disk, api.Capacity)
        self.assertEquals(2, swap_disk.value)
