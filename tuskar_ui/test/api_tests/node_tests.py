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

from mock import patch  # noqa

from novaclient.v1_1 import servers

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class NodeAPITests(test.APITestCase):
    def test_node_create(self):
        node = api.node.BareMetalNode(self.baremetalclient_nodes.first())

        with patch('novaclient.v1_1.contrib.baremetal.'
                   'BareMetalNodeManager.create',
                   return_value=node):
            ret_val = api.node.Node.create(
                self.request,
                node.driver_info['ipmi_address'],
                'i386',
                node.cpus,
                node.memory_mb,
                node.local_gb,
                ['aa:aa:aa:aa:aa:aa'],
                ipmi_username='admin',
                ipmi_password='password')

        self.assertIsInstance(ret_val, api.node.Node)

    def test_node_get(self):
        node = self.baremetalclient_nodes.first()
        instance = self.novaclient_servers.first()

        with patch('openstack_dashboard.api.nova.server_get',
                   return_value=instance):
            with patch('novaclient.v1_1.contrib.baremetal.'
                       'BareMetalNodeManager.find',
                       return_value=node):
                with patch('openstack_dashboard.api.nova.server_list',
                           return_value=([instance], False)):
                    ret_val = api.node.Node.get(self.request, node.uuid)
                    ret_instance = ret_val.instance

        self.assertIsInstance(ret_val, api.node.Node)
        self.assertIsInstance(ret_instance, servers.Server)

    def test_node_get_by_instance_uuid(self):
        instance = self.novaclient_servers.first()
        node = self.baremetalclient_nodes.first()
        nodes = self.baremetalclient_nodes.list()

        with patch('openstack_dashboard.api.nova.server_get',
                   return_value=instance):
            with patch('novaclient.v1_1.contrib.baremetal.'
                       'BareMetalNodeManager.list',
                       return_value=nodes):
                with patch('openstack_dashboard.api.nova.server_list',
                           return_value=([instance], False)):
                    ret_val = api.node.Node.get_by_instance_uuid(
                        self.request,
                        node.instance_uuid)
                    ret_instance = ret_val.instance

        self.assertIsInstance(ret_val, api.node.Node)
        self.assertIsInstance(ret_instance, servers.Server)

    def test_node_list(self):
        instances = self.novaclient_servers.list()
        nodes = self.baremetalclient_nodes.list()

        with patch('openstack_dashboard.api.nova.server_list',
                   return_value=(instances, None)):
            with patch('novaclient.v1_1.contrib.baremetal.'
                       'BareMetalNodeManager.list',
                       return_value=nodes):
                ret_val = api.node.Node.list(self.request)

        for node in ret_val:
            self.assertIsInstance(node, api.node.Node)
        self.assertEqual(6, len(ret_val))

    def test_node_delete(self):
        node = self.baremetalclient_nodes.first()
        with patch('novaclient.v1_1.contrib.baremetal.'
                   'BareMetalNodeManager.delete',
                   return_value=None):
            api.node.Node.delete(self.request, node.uuid)

    def test_node_set_maintenance(self):
        node = self.baremetalclient_nodes.first()
        with self.assertRaises(NotImplementedError):
            api.node.Node.set_maintenance(self.request, node.uuid, False)

    def test_node_set_power_state(self):
        node = self.baremetalclient_nodes.first()
        with self.assertRaises(NotImplementedError):
            api.node.Node.set_power_state(self.request, node.uuid, 'on')

    def test_node_instance(self):
        node = self.baremetalclient_nodes.first()
        instance = self.novaclient_servers.first()

        with patch('openstack_dashboard.api.nova.server_get',
                   return_value=instance):
            with patch('openstack_dashboard.api.nova.server_list',
                       return_value=([instance], False)):
                ret_val = api.node.Node(node).instance

        self.assertIsInstance(ret_val, servers.Server)

    def test_node_image_name(self):
        node = self.baremetalclient_nodes.first()
        instance = self.novaclient_servers.first()
        image = self.glanceclient_images.first()

        with patch('openstack_dashboard.api.nova.server_get',
                   return_value=instance):
            with patch('openstack_dashboard.api.glance.image_get',
                       return_value=image):
                with patch('openstack_dashboard.api.nova.server_list',
                           return_value=([instance], False)):
                    ret_val = api.node.Node(node).image_name
        self.assertEqual(ret_val, 'overcloud-control')

    def test_node_addresses_no_ironic(self):
        node = self.baremetalclient_nodes.first()
        ret_val = api.node.BareMetalNode(node).addresses
        self.assertEqual(2, len(ret_val))
