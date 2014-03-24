# -*- coding: utf8 -*-
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

from django.core import urlresolvers

from mock import patch, call  # noqa

from openstack_dashboard.test.test_data import utils
from tuskar_ui import api as api
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse('horizon:infrastructure:nodes:index')
REGISTER_URL = urlresolvers.reverse('horizon:infrastructure:nodes:register')
DETAIL_VIEW = 'horizon:infrastructure:nodes:detail'
TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)


class NodesTests(test.BaseAdminViewTests):
    @handle_errors("Error!", [])
    def _raise_tuskar_exception(self, request, *args, **kwargs):
        raise self.exceptions.tuskar

    def test_index_get(self):

        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['list'],  # Only allow these attributes
            'list.return_value': [],
        }) as mock:
            res = self.client.get(INDEX_URL)
            # FIXME(lsmola) optimize, this should call 1 time, what the hell
            self.assertEqual(mock.list.call_count, 8)

        self.assertTemplateUsed(
            res, 'infrastructure/nodes/index.html')
        self.assertTemplateUsed(res, 'infrastructure/nodes/_overview.html')

    def test_free_nodes(self):
        overcloud_role = api.OvercloudRole(
            TEST_DATA.tuskarclient_overcloud_roles.first())
        free_nodes = [api.Node(node)
                      for node in self.ironicclient_nodes.list()]
        for node in free_nodes:
            node.overcloud_role = overcloud_role

        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['list'],  # Only allow these attributes
            'list.return_value': free_nodes,
        }) as mock:
            res = self.client.get(INDEX_URL + '?tab=nodes__free')
            # FIXME(lsmola) horrible count, optimize
            self.assertEqual(mock.list.call_count, 10)

        self.assertTemplateUsed(res,
                                'infrastructure/nodes/index.html')
        self.assertTemplateUsed(res, 'horizon/common/_detail_table.html')
        self.assertItemsEqual(res.context['free_nodes_table'].data,
                              free_nodes)

    def test_free_nodes_list_exception(self):
        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['list'],
            'list.side_effect': self._raise_tuskar_exception,
        }) as mock:
            res = self.client.get(INDEX_URL + '?tab=nodes__free')
            self.assertEqual(mock.list.call_count, 3)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_deployed_nodes(self):
        deployed_nodes = [api.Node(node)
                          for node in self.ironicclient_nodes.list()]
        instance = TEST_DATA.novaclient_servers.first()
        overcloud_role = api.OvercloudRole(
            TEST_DATA.tuskarclient_overcloud_roles.first())
        for node in deployed_nodes:
            node.overcloud_role = overcloud_role

        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['list', 'instance'],  # Only allow these attributes
            'instance': instance,
            'list.return_value': deployed_nodes,
        }) as mock:
            res = self.client.get(INDEX_URL + '?tab=nodes__deployed')
            # FIXME(lsmola) horrible count, optimize
            self.assertEqual(mock.list.call_count, 10)

        self.assertTemplateUsed(
            res, 'infrastructure/nodes/index.html')
        self.assertTemplateUsed(res, 'horizon/common/_detail_table.html')
        self.assertItemsEqual(res.context['deployed_nodes_table'].data,
                              deployed_nodes)

    def test_deployed_nodes_list_exception(self):
        instance = TEST_DATA.novaclient_servers.first()
        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['list', 'instance'],
            'instance': instance,
            'list.side_effect': self._raise_tuskar_exception,
        }) as mock:
            res = self.client.get(INDEX_URL + '?tab=nodes__deployed')
            self.assertEqual(mock.list.call_count, 3)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_register_get(self):
        res = self.client.get(REGISTER_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/nodes/register.html')

    def test_register_post(self):
        node = TEST_DATA.ironicclient_nodes.first
        data = {
            'register_nodes-TOTAL_FORMS': 2,
            'register_nodes-INITIAL_FORMS': 1,
            'register_nodes-MAX_NUM_FORMS': 1000,

            'register_nodes-0-ipmi_address': '127.0.0.1',
            'register_nodes-0-mac_address': 'de:ad:be:ef:ca:fe',
            'register_nodes-0-cpus': '1',
            'register_nodes-0-memory': '2',
            'register_nodes-0-local_disk': '3',

            'register_nodes-1-ipmi_address': '127.0.0.2',
            'register_nodes-1-mac_address': 'de:ad:be:ef:ca:ff',
            'register_nodes-1-cpus': '4',
            'register_nodes-1-memory': '5',
            'register_nodes-1-local_disk': '6',
        }
        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['create'],
            'create.return_value': node,
        }) as Node:
            res = self.client.post(REGISTER_URL, data)
            request = Node.create.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Node.create.call_args_list, [
                call(request, '127.0.0.1', 1, 2, 3,
                     'DE:AD:BE:EF:CA:FE', None, u''),
                call(request, '127.0.0.2', 4, 5, 6,
                     'DE:AD:BE:EF:CA:FF', None, u''),
            ])
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_register_post_exception(self):
        data = {
            'register_nodes-TOTAL_FORMS': 2,
            'register_nodes-INITIAL_FORMS': 1,
            'register_nodes-MAX_NUM_FORMS': 1000,

            'register_nodes-0-ipmi_address': '127.0.0.1',
            'register_nodes-0-mac_address': 'de:ad:be:ef:ca:fe',
            'register_nodes-0-cpus': '1',
            'register_nodes-0-memory': '2',
            'register_nodes-0-local_disk': '3',

            'register_nodes-1-ipmi_address': '127.0.0.2',
            'register_nodes-1-mac_address': 'de:ad:be:ef:ca:ff',
            'register_nodes-1-cpus': '4',
            'register_nodes-1-memory': '5',
            'register_nodes-1-local_disk': '6',
        }
        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['create'],
            'create.side_effect': self.exceptions.tuskar,
        }) as Node:
            res = self.client.post(REGISTER_URL, data)
            request = Node.create.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Node.create.call_args_list, [
                call(request, '127.0.0.1', 1, 2, 3,
                     'DE:AD:BE:EF:CA:FE', None, u''),
                call(request, '127.0.0.2', 4, 5, 6,
                     'DE:AD:BE:EF:CA:FF', None, u''),
            ])
        self.assertTemplateUsed(
            res, 'infrastructure/nodes/register.html')

    def test_node_detail(self):
        node = api.Node(self.ironicclient_nodes.list()[0])

        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['get'],  # Only allow these attributes
            'get.return_value': node,
        }) as mock:
            res = self.client.get(
                urlresolvers.reverse(DETAIL_VIEW, args=(node.uuid,))
            )
            self.assertEqual(mock.get.call_count, 1)

        self.assertTemplateUsed(res, 'infrastructure/nodes/details.html')
        self.assertEqual(res.context['node'], node)

    def test_node_detail_exception(self):
        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['get'],
            'get.side_effect': self._raise_tuskar_exception,
        }) as mock:
            res = self.client.get(
                urlresolvers.reverse(DETAIL_VIEW, args=('no-such-node',))
            )
            self.assertEqual(mock.get.call_count, 1)

        self.assertRedirectsNoFollow(res, INDEX_URL)
