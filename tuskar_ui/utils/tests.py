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

from tuskar_ui.test import helpers
from tuskar_ui.utils import utils


class UtilsTests(helpers.TestCase):
    def test_de_camel_case(self):
        ret = utils.de_camel_case('CamelCaseString')
        self.assertEqual(ret, 'Camel Case String')
        ret = utils.de_camel_case('SecureSSLConnection')
        self.assertEqual(ret, 'Secure SSL Connection')
        ret = utils.de_camel_case('xxXXxx')
        self.assertEqual(ret, 'xx X Xxx')
        ret = utils.de_camel_case('XXX')
        self.assertEqual(ret, 'XXX')
        ret = utils.de_camel_case('NON Camel Case')
        self.assertEqual(ret, 'NON Camel Case')

    def test_list_to_dict(self):
        Item = collections.namedtuple('Item', 'id')
        ret = utils.list_to_dict([Item('foo'), Item('bar'), Item('bar')])
        self.assertEqual(ret, {'foo': Item('foo'), 'bar': Item('bar')})

    def test_length(self):
        ret = utils.length(iter([]))
        self.assertEqual(ret, 0)
        ret = utils.length(iter([1, 2, 3]))
        self.assertEqual(ret, 3)

    def test_check_image_type(self):
        Image = collections.namedtuple('Image', 'properties')
        ret = utils.check_image_type(Image({'type': 'Picasso'}), 'Picasso')
        self.assertTrue(ret)
        ret = utils.check_image_type(Image({'type': 'Picasso'}), 'Van Gogh')
        self.assertFalse(ret)
        ret = utils.check_image_type(Image({}), 'Van Gogh')
        self.assertTrue(ret)

    def test_filter_items(self):
        Item = collections.namedtuple('Item', 'index')
        items = [Item(i) for i in range(7)]
        ret = list(utils.filter_items(items, index=1))
        self.assertEqual(ret, [Item(1)])
        ret = list(utils.filter_items(items, index__in=(1, 2, 3)))
        self.assertEqual(ret, [Item(1), Item(2), Item(3)])
        ret = list(utils.filter_items(items, index__not_in=(1, 2, 3)))
        self.assertEqual(ret, [Item(0), Item(4), Item(5), Item(6)])

    def test_safe_int_cast(self):
        ret = utils.safe_int_cast(1)
        self.assertEqual(ret, 1)
        ret = utils.safe_int_cast('1')
        self.assertEqual(ret, 1)
        ret = utils.safe_int_cast('')
        self.assertEqual(ret, 0)
        ret = utils.safe_int_cast(None)
        self.assertEqual(ret, 0)
        ret = utils.safe_int_cast(object())
        self.assertEqual(ret, 0)
