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

import collections
import json

from tuskar_ui.infrastructure.templatetags import chart_helpers
from tuskar_ui.infrastructure.templatetags import icon_helpers
from tuskar_ui.test import helpers


Flavor = collections.namedtuple('Flavor', 'name used_instances')
Flavors = collections.namedtuple('Flavors', 'list_flavors')


class ChartHelpersTest(helpers.TestCase):
    def test_remaining_capacity_by_flavors(self):
        flavors = Flavors([
            Flavor('a', 0),
            Flavor('b', 1),
        ])
        ret = chart_helpers.remaining_capacity_by_flavors(flavors)
        self.assertEqual(
            ret,
            '<p>Capacity remaining by flavors: </p>'
            '<p><strong>0</strong> a</p> '
            '<p><strong>1</strong> b</p>'
        )

    def test_all_used_instances(self):
        flavors = Flavors([
            Flavor('a', 0),
            Flavor('b', 1),
        ])
        ret = chart_helpers.all_used_instances(flavors)
        self.assertEqual(ret, json.dumps([
            {
                'popup_used': '<p> 0% total, '
                              '<strong> 0 instances</strong> of a</p>',
                'used_instances': '0',
            }, {
                'popup_used': '<p> 1% total, '
                              '<strong> 1 instances</strong> of b</p>',
                'used_instances': '1',
            },
        ]))


class IconHelpersTest(helpers.TestCase):
    def test_iconized_ironic_node_state(self):
        ret = icon_helpers.iconized_ironic_node_state('active')
        self.assertEqual(
            ret,
            u'<span class="fa fa-play powerstate"></span>'
            '<span>powered on</span> ',
        )
        ret = icon_helpers.iconized_ironic_node_state('')
        self.assertEqual(
            ret,
            u'<span class="fa fa-question powerstate"></span>'
            '<span>&mdash;</span> ',
        )
