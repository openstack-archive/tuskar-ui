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

from tuskar_ui.test import helpers as test
from tuskar_ui.utils import utils


class TestItem(object):
    def __init__(self, index):
        self.index = index


class UtilsTests(test.TestCase):
    def test_filter_items(self):
        items = [TestItem(i) for i in range(7)]

        first = utils.filter_items(items, index=0)
        even = utils.filter_items(items, index__in=(0, 2, 4, 6))
        last_two = utils.filter_items(items, index__not_in=range(5))

        self.assertEqual(utils.length(first), 1)
        self.assertEqual(utils.length(even), 4)
        self.assertEqual(utils.length(last_two), 2)
