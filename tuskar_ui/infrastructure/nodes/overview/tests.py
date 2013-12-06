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
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:nodes.overview:index')
REGISTER_URL = urlresolvers.reverse(
    'horizon:infrastructure:nodes.overview:register')
TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)


class RegisterNodesTests(test.BaseAdminViewTests):
    def test_index_get(self):
        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/nodes/overview/index.html')

    def test_register_get(self):
        res = self.client.get(REGISTER_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/nodes/overview/register.html')

    def test_register_post(self):
        node = TEST_DATA.ironicclient_nodes.first
        data = {
            'register_nodes-TOTAL_FORMS': 2,
            'register_nodes-INITIAL_FORMS': 1,
            'register_nodes-MAX_NUM_FORMS': 1000,

            'register_nodes-0-ip_address': '127.0.0.1',
            'register_nodes-0-mac_address': 'de:ad:be:ef:ca:fe',
            'register_nodes-0-introspect_hardware': 'on',

            'register_nodes-1-ip_address': '127.0.0.2',
            'register_nodes-1-mac_address': 'de:ad:be:ef:ca:ff',
            'register_nodes-1-introspect_hardware': 'on',
        }
        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['create'],
            'create.return_value': node,
        }) as Node:
            res = self.client.post(REGISTER_URL, data)
            request = Node.create.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Node.create.call_args_list, [
                call(request, '127.0.0.1', None, None, None,
                     ['DE:AD:BE:EF:CA:FE'], None, u''),
                call(request, '127.0.0.2', None, None, None,
                     ['DE:AD:BE:EF:CA:FF'], None, u''),
            ])
        self.assertRedirectsNoFollow(res, INDEX_URL)
