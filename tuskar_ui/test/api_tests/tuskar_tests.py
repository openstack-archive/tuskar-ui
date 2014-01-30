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

from glanceclient.v1 import images
from heatclient.v1 import events
from heatclient.v1 import stacks
from novaclient.v1_1 import servers

from tuskar_ui import api
from tuskar_ui.test import helpers as test

# TODO(Tzu-Mainn Chen): uncomment mock data and mock
# api calls once api.py stops using mock data


class TuskarAPITests(test.APITestCase):

    def test_overcloud_create(self):
        #overcloud = self.tuskarclient_overclouds.first()

        ret_val = api.Overcloud.create(self.request, [])
        self.assertIsInstance(ret_val, api.Overcloud)

    def test_overcloud_list(self):
        #overclouds = self.tuskarclient_overclouds.list()

        ret_val = api.Overcloud.list(self.request)
        for oc in ret_val:
            self.assertIsInstance(oc, api.Overcloud)
        self.assertEqual(1, len(ret_val))

    def test_overcloud_get(self):
        overcloud = self.tuskarclient_overclouds.first()

        ret_val = api.Overcloud.get(self.request, overcloud['id'])
        self.assertIsInstance(ret_val, api.Overcloud)

    def test_overcloud_stack(self):
        overcloud = self.tuskarclient_overclouds.first()

        ret_val = api.Overcloud(overcloud).stack
        self.assertIsInstance(ret_val, stacks.Stack)

    def test_overcloud_stack_events(self):
        overcloud = self.tuskarclient_overclouds.first()

        ret_val = api.Overcloud(overcloud).stack_events
        for e in ret_val:
            self.assertIsInstance(e, events.Event)
        self.assertEqual(8, len(ret_val))

    def test_overcloud_stack_events_empty(self):
        overcloud = self.tuskarclient_overclouds.first()
        overcloud['stack_id'] = None

        ret_val = api.Overcloud(overcloud).stack_events
        self.assertListEqual([], ret_val)

    def test_overcloud_is_deployed(self):
        overcloud = self.tuskarclient_overclouds.first()

        ret_val = api.Overcloud(overcloud).is_deployed
        self.assertFalse(ret_val)

    def test_overcloud_resources(self):
        overcloud = self.tuskarclient_overclouds.first()
        category = self.tuskarclient_resource_categories.first()

        ret_val = api.Overcloud(overcloud).resources(
            api.ResourceCategory(category))
        for i in ret_val:
            self.assertIsInstance(i, api.Resource)
        self.assertEqual(1, len(ret_val))

    def test_node_create(self):
        node = self.ironicclient_nodes.first()

        ret_val = api.Node.create(
            self.request,
            node.driver_info['ipmi_address'],
            node.properties['cpu'],
            node.properties['ram'],
            node.properties['local_disk'],
            ['aa:aa:aa:aa:aa:aa'],
            ipmi_username='admin',
            ipmi_password='password')
        ret_val.instance_uuid = None

        self.assertIsInstance(ret_val, api.Node)
        self.assertIsNone(ret_val.instance)

    def test_node_get(self):
        node = self.ironicclient_nodes.first()

        ret_val = api.Node.get(self.request, node.uuid)
        self.assertIsInstance(ret_val, api.Node)
        self.assertIsInstance(ret_val.instance, servers.Server)

    def test_node_get_by_instance_uuid(self):
        node = self.ironicclient_nodes.first()

        ret_val = api.Node.get_by_instance_uuid(self.request,
                                                node.instance_uuid)
        self.assertIsInstance(ret_val, api.Node)
        self.assertIsInstance(ret_val.instance, servers.Server)

    def test_node_list(self):
        #nodes = self.tuskarclient_overclouds.list()

        ret_val = api.Node.list(self.request)
        for node in ret_val:
            self.assertIsInstance(node, api.Node)
        self.assertEqual(5, len(ret_val))

    def test_node_delete(self):
        node = self.ironicclient_nodes.first()

        api.Node.delete(self.request, node.uuid)

    def test_node_addresses(self):
        node = self.ironicclient_nodes.first()

        ret_val = api.Node(node).addresses
        self.assertEqual(2, len(ret_val))

    def test_resource_get(self):
        overcloud = self.tuskarclient_overclouds.first()
        resource = self.heatclient_resources.first()

        ret_val = api.Resource.get(self.request, overcloud,
                                   resource.resource_name)
        self.assertIsInstance(ret_val, api.Resource)

    def test_resource_node(self):
        resource = self.heatclient_resources.first()

        ret_val = api.Resource(resource).node
        self.assertIsInstance(ret_val, api.Node)
        self.assertIsInstance(ret_val.instance, servers.Server)

    def test_resource_category_list(self):
        #categories = self.tuskarclient_resource_categories.list()

        ret_val = api.ResourceCategory.list(self.request)
        for c in ret_val:
            self.assertIsInstance(c, api.ResourceCategory)
        self.assertEqual(4, len(ret_val))

    def test_resource_category_get(self):
        category = self.tuskarclient_resource_categories.first()

        ret_val = api.ResourceCategory.get(self.request, category['id'])
        self.assertIsInstance(ret_val, api.ResourceCategory)

    def test_resource_category_image(self):
        category = self.tuskarclient_resource_categories.first()

        ret_val = api.ResourceCategory(category).image
        self.assertIsInstance(ret_val, images.Image)
