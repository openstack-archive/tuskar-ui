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
from horizon import exceptions as horizon_exceptions
from mock import patch, call, ANY  # noqa
from openstack_dashboard.test import helpers
from openstack_dashboard.test.test_data import utils

from tuskar_ui import api
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.infrastructure.nodes import forms
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


class NodesTests(
    test.NodesTestMixin,
    test.BaseAdminViewTests,
):
    @handle_errors("Error!", [])
    def _raise_tuskar_exception(self, request, *args, **kwargs):
        raise self.exceptions.tuskar

    @handle_errors("Error!", [])
    def _raise_horizon_exception_not_found(self, request, *args, **kwargs):
        raise horizon_exceptions.NotFound

    def test_index_get(self):
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['list'],
            'list.return_value': [],
        }) as mock:
            res = self.client.get(INDEX_URL)
            self.assertEqual(mock.list.call_count, 3)

        self.assertTemplateUsed(
            res, 'infrastructure/nodes/index.html')
        self.assertTemplateUsed(res, 'infrastructure/nodes/_overview.html')

    def _all_mocked_nodes(self):
        return [api.node.Node(api.node.IronicNode(node))
                for node in self.ironicclient_nodes.list()]

    def _test_index_tab(self, tab_name, nodes):
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['list'],
            'list.return_value': nodes,
        }) as Node:
            res = self.client.get(INDEX_URL + '?tab=nodes__' + tab_name)
            self.assertEqual(Node.list.call_count, 3)

        self.assertTemplateUsed(
            res, 'infrastructure/nodes/index.html')
        self.assertTemplateUsed(res, 'horizon/common/_detail_table.html')
        self.assertItemsEqual(
            res.context[tab_name + '_nodes_table_table'].data,
            nodes)

    def test_all_nodes(self):
        nodes = self._all_mocked_nodes()
        self._test_index_tab('all', nodes)

    def test_provisioned_nodes(self):
        nodes = self._all_mocked_nodes()
        self._test_index_tab('provisioned', nodes)

    def test_free_nodes(self):
        nodes = self._all_mocked_nodes()
        self._test_index_tab('free', nodes)

    def test_maintenance_nodes(self):
        nodes = self._all_mocked_nodes()[6:]
        self._test_index_tab('maintenance', nodes)

    def _test_index_tab_list_exception(self, tab_name):
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['list'],
            'list.side_effect': self._raise_tuskar_exception,
        }) as mock:
            res = self.client.get(INDEX_URL + '?tab=nodes__' + tab_name)
            self.assertEqual(mock.list.call_count, 2)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_all_nodes_list_exception(self):
        self._test_index_tab_list_exception('all')

    def test_provisioned_nodes_list_exception(self):
        self._test_index_tab_list_exception('provisioned')

    def test_free_nodes_list_exception(self):
        self._test_index_tab_list_exception('free')

    def test_maintenance_nodes_list_exception(self):
        self._test_index_tab_list_exception('maintenance')

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

            'register_nodes-0-driver': 'pxe_ipmitool',
            'register_nodes-0-ipmi_address': '127.0.0.1',
            'register_nodes-0-ipmi_username': 'username',
            'register_nodes-0-ipmi_password': 'password',
            'register_nodes-0-mac_addresses': 'de:ad:be:ef:ca:fe',
            'register_nodes-0-cpu_arch': 'x86',
            'register_nodes-0-cpus': '1',
            'register_nodes-0-memory_mb': '2',
            'register_nodes-0-local_gb': '3',

            'register_nodes-1-driver': 'pxe_ipmitool',
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
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            self.assertListEqual(Node.create.call_args_list, [
                call(
                    ANY,
                    ipmi_address=u'127.0.0.1',
                    cpu_arch='x86',
                    cpus=1,
                    memory_mb=2,
                    local_gb=3,
                    mac_addresses=['DE:AD:BE:EF:CA:FE'],
                    ipmi_username=u'username',
                    ipmi_password=u'password',
                    driver='pxe_ipmitool',
                ),
                call(
                    ANY,
                    ipmi_address=u'127.0.0.2',
                    cpu_arch='x86',
                    cpus=4,
                    memory_mb=5,
                    local_gb=6,
                    mac_addresses=['DE:AD:BE:EF:CA:FF'],
                    ipmi_username=None,
                    ipmi_password=None,
                    driver='pxe_ipmitool',
                ),
            ])

    def test_register_post_exception(self):
        data = {
            'register_nodes-TOTAL_FORMS': 2,
            'register_nodes-INITIAL_FORMS': 1,
            'register_nodes-MAX_NUM_FORMS': 1000,

            'register_nodes-0-driver': 'pxe_ipmitool',
            'register_nodes-0-ipmi_address': '127.0.0.1',
            'register_nodes-0-ipmi_username': 'username',
            'register_nodes-0-ipmi_password': 'password',
            'register_nodes-0-mac_addresses': 'de:ad:be:ef:ca:fe',
            'register_nodes-0-cpu_arch': 'x86',
            'register_nodes-0-cpus': '1',
            'register_nodes-0-memory_mb': '2',
            'register_nodes-0-local_gb': '3',

            'register_nodes-1-driver': 'pxe_ipmitool',
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
            self.assertListEqual(Node.create.call_args_list, [
                call(
                    ANY,
                    ipmi_address=u'127.0.0.1',
                    cpu_arch='x86',
                    cpus=1,
                    memory_mb=2,
                    local_gb=3,
                    mac_addresses=['DE:AD:BE:EF:CA:FE'],
                    ipmi_username=u'username',
                    ipmi_password=u'password',
                    driver='pxe_ipmitool',
                ),
                call(
                    ANY,
                    ipmi_address=u'127.0.0.2',
                    cpu_arch='x86',
                    cpus=4,
                    memory_mb=5,
                    local_gb=6,
                    mac_addresses=['DE:AD:BE:EF:CA:FF'],
                    ipmi_username=None,
                    ipmi_password=None,
                    driver='pxe_ipmitool',
                ),
            ])
        self.assertTemplateUsed(
            res, 'infrastructure/nodes/register.html')

    def test_node_detail(self):
        node = api.node.Node(self.ironicclient_nodes.list()[0])

        with contextlib.nested(
            patch('tuskar_ui.api.node.Node', **{
                'spec_set': ['get'],
                'get.return_value': node,
            }),
            patch('tuskar_ui.api.heat.Resource', **{
                'spec_set': ['get_by_node'],
                'get_by_node.side_effect': lambda *args, **kwargs: {}[None],
                # Raises LookupError
            }),
        ) as (mock_node, mock_heat):
            res = self.client.get(
                urlresolvers.reverse(DETAIL_VIEW, args=(node.uuid,))
            )
            self.assertEqual(mock_node.get.call_count, 1)

        self.assertTemplateUsed(res, 'infrastructure/nodes/detail.html')
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

    def test_node_set_power_on(self):
        all_nodes = [api.node.Node(api.node.IronicNode(node))
                     for node in self.ironicclient_nodes.list()]
        node = all_nodes[6]
        roles = [api.tuskar.Role(r)
                 for r in TEST_DATA.tuskarclient_roles.list()]
        instance = TEST_DATA.novaclient_servers.first()
        image = TEST_DATA.glanceclient_images.first()
        data = {'action': "all_nodes_table__set_power_state_on__{0}".format(
            node.uuid)}

        with contextlib.nested(
            patch('tuskar_ui.api.node.NodeClient', **{
                'spec_set': ['ironic_enabled'],
                'ironic_enabled.return_value': True,
            }),
            patch('tuskar_ui.api.node.Node', **{
                'spec_set': ['list', 'set_power_state'],
                'list.return_value': all_nodes,
                'set_power_state.return_value': node,
            }),
            patch('tuskar_ui.api.tuskar.Role', **{
                'spec_set': ['list', 'name'],
                'list.return_value': roles,
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
                'spec_set': ['get_by_node', 'list_all_resources'],
                'get_by_node.side_effect': (
                    self._raise_horizon_exception_not_found),
                'list_all_resources.return_value': [],
            }),
        ) as (mock_node_client, mock_node, mock_role, mock_nova, mock_glance,
              mock_resource):
            res = self.client.post(INDEX_URL + '?tab=nodes__all', data)
            self.assertNoFormErrors(res)
            self.assertEqual(mock_node.set_power_state.call_count, 1)
            self.assertRedirectsNoFollow(res,
                                         INDEX_URL + '?tab=nodes__all')

    def test_node_set_power_off(self):
        all_nodes = [api.node.Node(api.node.IronicNode(node))
                     for node in self.ironicclient_nodes.list()]
        node = all_nodes[8]
        roles = [api.tuskar.Role(r)
                 for r in TEST_DATA.tuskarclient_roles.list()]
        instance = TEST_DATA.novaclient_servers.first()
        image = TEST_DATA.glanceclient_images.first()
        data = {'action': "all_nodes_table__set_power_state_off__{0}".format(
            node.uuid)}

        with contextlib.nested(
            patch('tuskar_ui.api.node.NodeClient', **{
                'spec_set': ['ironic_enabled'],
                'ironic_enabled.return_value': True,
            }),
            patch('tuskar_ui.api.node.Node', **{
                'spec_set': ['list', 'set_power_state'],
                'list.return_value': all_nodes,
                'set_power_state.return_value': node,
            }),
            patch('tuskar_ui.api.tuskar.Role', **{
                'spec_set': ['list', 'name'],
                'list.return_value': roles,
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
                'spec_set': ['get_by_node', 'list_all_resources'],
                'get_by_node.side_effect': (
                    self._raise_horizon_exception_not_found),
                'list_all_resources.return_value': [],
            }),
        ) as (mock_node_client, mock_node, mock_role, mock_nova, mock_glance,
              mock_resource):
            res = self.client.post(INDEX_URL + '?tab=nodes__all', data)
            self.assertNoFormErrors(res)
            self.assertEqual(mock_node.set_power_state.call_count, 1)
            self.assertRedirectsNoFollow(res,
                                         INDEX_URL + '?tab=nodes__all')

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
            }),
            patch('tuskar_ui.utils.metering.query_data',
                  return_value=([], 'unit')),
        ):
            url = urlresolvers.reverse(PERFORMANCE_VIEW, args=(node.uuid,))
            url += '?meter=cpu&date_options=7'
            res = self.client.get(url)

        json_content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertIn('series', json_content)
        self.assertIn('settings', json_content)

    def test_get_driver_info_dict(self):
        data = {
            'driver': 'pxe_ipmitool',
            'ipmi_address': '127.0.0.1',
            'ipmi_username': 'root',
            'ipmi_password': 'P@55W0rd',
        }
        ret = forms.get_driver_info_dict(data)
        self.assertEqual(ret, {
            'driver': 'pxe_ipmitool',
            'ipmi_address': '127.0.0.1',
            'ipmi_username': 'root',
            'ipmi_password': 'P@55W0rd',
        })
        data = {
            'driver': 'pxe_ssh',
            'ssh_address': '127.0.0.1',
            'ssh_username': 'root',
            'ssh_key_contents': 'P@55W0rd',
        }
        ret = forms.get_driver_info_dict(data)
        self.assertEqual(ret, {
            'driver': 'pxe_ssh',
            'ssh_address': '127.0.0.1',
            'ssh_username': 'root',
            'ssh_key_contents': 'P@55W0rd',
        })

    def test_create_node(self):
        data = {
            'ipmi_address': '127.0.0.1',
            'cpu_arch': 'x86',
            'cpus': 1,
            'memory_mb': 2,
            'local_gb': 3,
            'mac_addresses': 'DE:AD:BE:EF:CA:FE',
            'ipmi_username': 'username',
            'ipmi_password': 'password',
            'driver': 'pxe_ipmitool',
        }
        with patch('tuskar_ui.api.node.Node', **{
            'spec_set': ['create', 'set_maintenance', 'discover'],
            'create.return_value': None,
        }) as Node:
            forms.create_node(None, data)
            self.assertListEqual(Node.create.call_args_list, [
                call(
                    ANY,
                    ipmi_address=u'127.0.0.1',
                    cpu_arch='x86',
                    cpus=1,
                    memory_mb=2,
                    local_gb=3,
                    mac_addresses=['DE:AD:BE:EF:CA:FE'],
                    ipmi_username=u'username',
                    ipmi_password=u'password',
                    driver='pxe_ipmitool',
                ),
            ])
