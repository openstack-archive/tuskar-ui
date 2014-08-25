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

import contextlib
import json

from django.core import urlresolvers

from mock import patch, call  # noqa

from horizon import exceptions as horizon_exceptions
from openstack_dashboard.test import helpers
from openstack_dashboard.test.test_data import utils
from tuskar_ui import api
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import heat_data
from tuskar_ui.test.test_data import node_data
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse('horizon:infrastructure:nodes:index')
REGISTER_URL = urlresolvers.reverse('horizon:infrastructure:nodes:register')
DETAIL_VIEW = 'horizon:infrastructure:nodes:detail'
PERFORMANCE_VIEW = 'horizon:infrastructure:nodes:performance'
TEST_DATA = utils.TestDataContainer()
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)


class NodesTests(test.BaseAdminViewTests, helpers.APITestCase):
    @handle_errors("Error!", [])
    def _raise_tuskar_exception(self, request, *args, **kwargs):
        raise self.exceptions.tuskar

    @handle_errors("Error!", [])
    def _raise_horizon_exception_not_found(self, request, *args, **kwargs):
        raise horizon_exceptions.NotFound

    def test_index_get(self):

        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['list'],  # Only allow these attributes
            'list.return_value': [],
        }) as mock:
            res = self.client.get(INDEX_URL)
            # FIXME(lsmola) optimize, this should call 1 time, what the hell
            self.assertEqual(mock.list.call_count, 5)

        self.assertTemplateUsed(
            res, 'infrastructure/nodes/index.html')
        self.assertTemplateUsed(res, 'infrastructure/nodes/_overview.html')

    def test_registered_nodes(self):
        registered_nodes = [api.node.Node(api.node.IronicNode(node))
                            for node in self.ironicclient_nodes.list()]
        roles = [api.tuskar.OvercloudRole(r)
                 for r in TEST_DATA.tuskarclient_roles.list()]
        instance = TEST_DATA.novaclient_servers.first()
        image = TEST_DATA.glanceclient_images.first()

        # TODO(akrivoka): this should be placed in the test data, but currently
        # that's not possible due to the drawbacks in the Node architecture.
        # We should rework the entire api/node.py and fix this problem.
        for node in registered_nodes:
            node.ip_address = '1.1.1.1'

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': ['list', 'name'],
                'list.return_value': roles,
            }),
            patch('tuskar_ui.api.node.Node', **{
                'spec_set': ['list'],
                'list.return_value': registered_nodes,
            }),
            patch('tuskar_ui.api.node.nova', **{
                'spec_set': ['server_get', 'server_list'],
                'server_get.return_value': instance,
                'server_list.return_value': ([instance], False),
            }),
            patch('tuskar_ui.api.node.glance', **{
                'spec_set': ['image_get'],
                'image_get.return_value': image,
            }),
            patch('tuskar_ui.api.heat.Resource', **{
                'spec_set': ['get_by_node'],  # Only allow these attributes
                'get_by_node.side_effect': (
                    self._raise_horizon_exception_not_found),
            }),
        ) as (_OvercloudRole, Node, _nova, _glance, _resource):
            res = self.client.get(INDEX_URL + '?tab=nodes__registered')
            # FIXME(lsmola) horrible count, optimize
            self.assertEqual(Node.list.call_count, 6)

        self.assertTemplateUsed(
            res, 'infrastructure/nodes/index.html')
        self.assertTemplateUsed(res, 'horizon/common/_detail_table.html')
        self.assertItemsEqual(res.context['nodes_table_table'].data,
                              registered_nodes)

    def test_registered_nodes_list_exception(self):
        instance = TEST_DATA.novaclient_servers.first()
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['list', 'instance'],
            'instance': instance,
            'list.side_effect': self._raise_tuskar_exception,
        }) as mock:
            res = self.client.get(INDEX_URL + '?tab=nodes__registered')
            self.assertEqual(mock.list.call_count, 4)

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

            'register_nodes-0-driver': 'ipmi',
            'register_nodes-0-ipmi_address': '127.0.0.1',
            'register_nodes-0-ipmi_username': 'username',
            'register_nodes-0-ipmi_password': 'password',
            'register_nodes-0-mac_addresses': 'de:ad:be:ef:ca:fe',
            'register_nodes-0-cpu_arch': 'x86',
            'register_nodes-0-cpus': '1',
            'register_nodes-0-memory_mb': '2',
            'register_nodes-0-local_gb': '3',

            'register_nodes-1-driver': 'ipmi',
            'register_nodes-1-ipmi_address': '127.0.0.2',
            'register_nodes-1-mac_addresses': 'de:ad:be:ef:ca:ff',
            'register_nodes-1-cpu_arch': 'x86',
            'register_nodes-1-cpus': '4',
            'register_nodes-1-memory_mb': '5',
            'register_nodes-1-local_gb': '6',
        }
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['create'],
            'create.return_value': node,
        }) as Node:
            res = self.client.post(REGISTER_URL, data)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            request = Node.create.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Node.create.call_args_list, [
                call(
                    request,
                    ipmi_address=u'127.0.0.1',
                    cpu_arch='x86',
                    cpus=1,
                    memory_mb=2,
                    local_gb=3,
                    mac_addresses=['DE:AD:BE:EF:CA:FE'],
                    ipmi_username=u'username',
                    ipmi_password=u'password',
                    driver='ipmi',
                ),
                call(
                    request,
                    ipmi_address=u'127.0.0.2',
                    cpu_arch='x86',
                    cpus=4,
                    memory_mb=5,
                    local_gb=6,
                    mac_addresses=['DE:AD:BE:EF:CA:FF'],
                    ipmi_username=None,
                    ipmi_password=None,
                    driver='ipmi',
                ),
            ])

    def test_register_post_exception(self):
        data = {
            'register_nodes-TOTAL_FORMS': 2,
            'register_nodes-INITIAL_FORMS': 1,
            'register_nodes-MAX_NUM_FORMS': 1000,

            'register_nodes-0-driver': 'ipmi',
            'register_nodes-0-ipmi_address': '127.0.0.1',
            'register_nodes-0-ipmi_username': 'username',
            'register_nodes-0-ipmi_password': 'password',
            'register_nodes-0-mac_addresses': 'de:ad:be:ef:ca:fe',
            'register_nodes-0-cpu_arch': 'x86',
            'register_nodes-0-cpus': '1',
            'register_nodes-0-memory_mb': '2',
            'register_nodes-0-local_gb': '3',

            'register_nodes-1-driver': 'ipmi',
            'register_nodes-1-ipmi_address': '127.0.0.2',
            'register_nodes-1-mac_addresses': 'de:ad:be:ef:ca:ff',
            'register_nodes-1-cpu_arch': 'x86',
            'register_nodes-1-cpus': '4',
            'register_nodes-1-memory_mb': '5',
            'register_nodes-1-local_gb': '6',
        }
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['create'],
            'create.side_effect': self.exceptions.tuskar,
        }) as Node:
            res = self.client.post(REGISTER_URL, data)
            self.assertEqual(res.status_code, 200)
            request = Node.create.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Node.create.call_args_list, [
                call(
                    request,
                    ipmi_address=u'127.0.0.1',
                    cpu_arch='x86',
                    cpus=1,
                    memory_mb=2,
                    local_gb=3,
                    mac_addresses=['DE:AD:BE:EF:CA:FE'],
                    ipmi_username=u'username',
                    ipmi_password=u'password',
                    driver='ipmi',
                ),
                call(
                    request,
                    ipmi_address=u'127.0.0.2',
                    cpu_arch='x86',
                    cpus=4,
                    memory_mb=5,
                    local_gb=6,
                    mac_addresses=['DE:AD:BE:EF:CA:FF'],
                    ipmi_username=None,
                    ipmi_password=None,
                    driver='ipmi',
                ),
            ])
        self.assertTemplateUsed(
            res, 'infrastructure/nodes/register.html')

    def test_node_detail(self):
        node = api.node.Node(self.ironicclient_nodes.list()[0])

        with contextlib.nested(
            patch('tuskar_ui.api.node.Node', **{
                'spec_set': ['get'],  # Only allow these attributes
                'get.return_value': node,
            }),
            patch('tuskar_ui.api.heat.Resource', **{
                'spec_set': ['get_by_node'],  # Only allow these attributes
                'get_by_node.side_effect': (
                    self._raise_horizon_exception_not_found),
            }),
        ) as (mock_node, mock_heat):
            res = self.client.get(
                urlresolvers.reverse(DETAIL_VIEW, args=(node.uuid,))
            )
            self.assertEqual(mock_node.get.call_count, 1)

        self.assertTemplateUsed(res, 'infrastructure/nodes/details.html')
        self.assertEqual(res.context['node'], node)

    def test_node_detail_exception(self):
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['get'],
            'get.side_effect': self._raise_tuskar_exception,
        }) as mock:
            res = self.client.get(
                urlresolvers.reverse(DETAIL_VIEW, args=('no-such-node',))
            )
            self.assertEqual(mock.get.call_count, 1)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_performance(self):
        node = api.node.Node(self.ironicclient_nodes.list()[0])
        instance = TEST_DATA.novaclient_servers.first()

        ceilometerclient = self.stub_ceilometerclient()
        ceilometerclient.resources = self.mox.CreateMockAnything()
        ceilometerclient.meters = self.mox.CreateMockAnything()

        self.mox.ReplayAll()

        with contextlib.nested(
            patch('tuskar_ui.api.node.Node', **{
                'spec_set': ['get'],
                'get.return_value': node,
            }),
            patch('tuskar_ui.api.node.nova', **{
                'spec_set': ['servers', 'server_get', 'server_list'],
                'servers.return_value': [instance],
                'server_list.return_value': ([instance], None),
            })
        ):
            url = urlresolvers.reverse(PERFORMANCE_VIEW, args=(node.uuid,))
            url += '?meter=cpu&date_options=7'
            res = self.client.get(url)

        json_content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertIn('series', json_content)
        self.assertIn('settings', json_content)
