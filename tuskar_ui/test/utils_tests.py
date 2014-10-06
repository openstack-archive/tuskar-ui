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

import mock

from tuskar_ui import api
from tuskar_ui.test import helpers as test
from tuskar_ui.utils import utils


class UtilsTests(test.APITestCase):
    def test_filter_items(self):
        nodes = self.baremetalclient_nodes.list()
        nodes = [api.node.BareMetalNode(node) for node in nodes]
        num_nodes = len(nodes)

        with mock.patch('novaclient.v1_1.contrib.baremetal.'
                        'BareMetalNodeManager.list', return_value=nodes):
            healthy_nodes = utils.filter_items(
                nodes, power_state__not_in=api.node.ERROR_STATES)
            defective_nodes = utils.filter_items(
                nodes, power_state__in=api.node.ERROR_STATES)
        self.assertEqual(sum(1 for _node in healthy_nodes), num_nodes - 1)
        self.assertEqual(sum(1 for _node in defective_nodes), 1)
