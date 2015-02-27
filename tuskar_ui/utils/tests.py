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
import datetime

import mock

from tuskar_ui.test import helpers
from tuskar_ui.utils import metering
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


class MeteringTests(helpers.TestCase):
    def test_query_data(self):
        Meter = collections.namedtuple('Meter', 'name unit')
        request = 'request'
        from_date = datetime.datetime(2015, 1, 1, 13, 45)
        to_date = datetime.datetime(2015, 1, 2, 13, 45)
        with mock.patch(
            'openstack_dashboard.api.ceilometer.meter_list',
            return_value=[Meter('foo.bar', u'µD')],
        ), mock.patch(
            'openstack_dashboard.api.ceilometer.CeilometerUsage',
            return_value=mock.MagicMock(**{
                'resource_aggregates_with_statistics.return_value': 'plonk',
            }),
        ):
            ret = metering.query_data(request, from_date, to_date,
                                      'all', 'foo.bar')
        self.assertEqual(ret, 'plonk')

    def test_url_part(self):
        ret = metering.url_part('foo_bar_baz', True)
        self.assertTrue('meter=foo_bar_baz' in ret)
        self.assertTrue('barchart=True' in ret)
        ret = metering.url_part('foo_bar_baz', False)
        self.assertTrue('meter=foo_bar_baz' in ret)
        self.assertFalse('barchart=True' in ret)

    def test_get_meter_name(self):
        ret = metering.get_meter_name('foo.bar.baz')
        self.assertEqual(ret, 'foo_bar_baz')

    def test_get_meters(self):
        ret = metering.get_meters(['foo.bar', 'foo.baz'])
        self.assertEqual(ret, [('foo.bar', 'foo_bar'), ('foo.baz', 'foo_baz')])

    def test_get_barchart_stats(self):
        series = [
            {'data': [{'x': 1, 'y': 1}, {'x': 4, 'y': 4}]},
            {'data': [{'x': 2, 'y': 2}, {'x': 5, 'y': 5}]},
            {'data': [{'x': 3, 'y': 3}, {'x': 6, 'y': 6}]},
        ]
        # Arrogance is measured in IT in micro-Dijkstras, µD.
        average, used, tooltip_average = metering.get_barchart_stats(series,
                                                                     u'µD')
        self.assertEqual(average, 2)
        self.assertEqual(used, 4)
        self.assertEqual(tooltip_average, u'Average 2 µD<br> From: 1, to: 4')

    def test_create_json_output(self):
        ret = metering.create_json_output([], False, u'µD', None, None)
        self.assertEqual(ret, {
            'series': [],
            'settings': {
                'higlight_last_point': True,
                'axes_x': False,
                'axes_y': True,
                'xMin': '',
                'renderer': 'StaticAxes',
                'xMax': '',
                'axes_y_label': False,
                'auto_size': False,
                'auto_resize': False,
            },
        })

        series = [
            {'data': [{'x': 1, 'y': 1}, {'x': 4, 'y': 4}]},
            {'data': [{'x': 2, 'y': 2}, {'x': 5, 'y': 5}]},
            {'data': [{'x': 3, 'y': 3}, {'x': 6, 'y': 6}]},
        ]
        ret = metering.create_json_output(series, True, u'µD', None, None)
        self.assertEqual(ret, {
            'series': series,
            'stats': {
                'average': 2,
                'used': 4,
                'tooltip_average': u'Average 2 µD<br> From: 1, to: 4',
            },
            'settings': {
                'yMin': 0,
                'yMax': 100,
                'higlight_last_point': True,
                'axes_x': False,
                'axes_y': True,
                'bar_chart_settings': {
                    'color_scale_domain': [0, 80, 80, 100],
                    'orientation': 'vertical',
                    'color_scale_range': [
                        '#0000FF',
                        '#0000FF',
                        '#FF0000',
                        '#FF0000',
                    ],
                    'width': 30,
                    'average_color_scale_domain': [0, 100],
                    'used_label_placement': 'left',
                    'average_color_scale_range': ['#0000FF', '#0000FF'],
                },
                'xMin': '',
                'renderer': 'StaticAxes',
                'xMax': '',
                'axes_y_label': False,
                'auto_size': False,
                'auto_resize': False,
            },
        })

    def test_get_nodes_stats(self):
        request = 'request'
        with mock.patch(
            'tuskar_ui.utils.metering.create_json_output',
            return_value='',
        ) as create_json_output, mock.patch(
            'tuskar_ui.utils.metering.query_data',
            return_value=[],
        ), mock.patch(
            'openstack_dashboard.utils.metering.series_for_meter',
            return_value=[],
        ), mock.patch(
            'openstack_dashboard.utils.metering.calc_date_args',
            return_value=('from date', 'to date'),
        ):
            ret = metering.get_nodes_stats(request, 'abc', 'def', 'foo.bar')
        self.assertEqual(ret, '')
        self.assertEqual(create_json_output.call_args_list, [
            mock.call([], None, '', 'from date', 'to date')
        ])
