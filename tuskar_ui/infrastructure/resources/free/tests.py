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

from mock import patch  # noqa

from tuskar_ui.test import helpers as test


INDEX_URL = urlresolvers.reverse('horizon:infrastructure:resources.free'
                                 ':index')
RESOURCES_OVERVIEW_URL = urlresolvers.reverse('horizon:infrastructure:'
                                              'resources.overview:index')


class FreeNodesTests(test.BaseAdminViewTests):
    def setUp(self):
        super(FreeNodesTests, self).setUp()

    def test_index(self):
        free_nodes = self.ironicclient_nodes.list()

        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['list'],  # Only allow these attributes
            'list.return_value': free_nodes,
        }) as mock:
            res = self.client.get(INDEX_URL)
            self.assertEqual(mock.list.call_count, 1)

        self.maxDiff = None
        self.assertTemplateUsed(res,
                                'infrastructure/resources.free/index.html')
        self.assertItemsEqual(res.context['free_nodes_table'].data,
                              free_nodes)

    def test_index_nodes_list_exception(self):
        with patch('tuskar_ui.api.Node', **{
            'spec_set': ['list'],
            'list.side_effect': self.exceptions.tuskar,
        }) as mock:
            res = self.client.get(INDEX_URL)
            self.assertEqual(mock.list.call_count, 1)

        self.assertRedirectsNoFollow(res, RESOURCES_OVERVIEW_URL)
