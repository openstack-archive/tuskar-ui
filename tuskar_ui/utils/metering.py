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

import copy

from datetime import datetime  # noqa
from datetime import timedelta  # noqa

from django.utils.http import urlencode
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

from openstack_dashboard.api import ceilometer
from openstack_dashboard.dashboards.admin.metering import views as metering


SETTINGS = {
    'settings': {
        'renderer': 'StaticAxes',
        'xMin': None,
        'xMax': None,
        'higlight_last_point': True,
        'auto_size': False,
        'auto_resize': False,
        'axes_x': False,
        'axes_y': True,
        'axes_y_label': False,
        'bar_chart_settings': {
            'orientation': 'vertical',
            'used_label_placement': 'left',
            'width': 30,
            'color_scale_domain': [0, 80, 80, 100],
            'color_scale_range': [
                '#0000FF',
                '#0000FF',
                '#FF0000',
                '#FF0000'
            ],
            'average_color_scale_domain': [0, 100],
            'average_color_scale_range': ['#0000FF', '#0000FF']
        }
    },
    'stats': {
        'average': None,
        'used': None,
        'tooltip_average': None,
    }
}


#TODO(lsmola) this should probably live in Horizon common
def query_data(request,
               date_from,
               date_to,
               group_by,
               meter,
               period=None,
               query=None,
               additional_query=None):

    if not period:
        period = _calc_period(date_from, date_to, 50)
    if additional_query is None:
        additional_query = []
    if date_from:
        additional_query += [{'field': 'timestamp',
                              'op': 'ge',
                              'value': date_from}]
    if date_to:
        additional_query += [{'field': 'timestamp',
                              'op': 'le',
                              'value': date_to}]

    # TODO(lsmola) replace this by logic implemented in I1 in bugs
    # 1226479 and 1226482, this is just a quick fix for RC1
    try:
        meter_list = [m for m in metering.meter_list(request)
                      if m.name == meter]
        unit = meter_list[0].unit
    except Exception:
        unit = ""
    if group_by == "resources":
        # TODO(lsmola) need to implement group_by groups of resources
        resources = []
        unit = ""
    else:
        ceilometer_usage = ceilometer.CeilometerUsage(request)
        try:
            resources = ceilometer_usage.resources_with_statistics(
                query, [meter], period=period, stats_attr=None,
                additional_query=additional_query)
        except Exception:
            resources = []
            exceptions.handle(request,
                              _('Unable to retrieve statistics.'))
    return resources, unit


#TODO(lsmola) push this function to Horizon common then delete this
def _calc_period(date_from, date_to, number_of_samples=400):
    if date_from and date_to:
        if date_to < date_from:
            # TODO(lsmola) propagate the Value error through Horizon
            # handler to the client with verbose message.
            raise ValueError("Date to must be bigger than date "
                             "from.")
            # get the time delta in seconds
        delta = date_to - date_from
        delta_in_seconds = delta.days * 24 * 3600 + delta.seconds

        period = delta_in_seconds / number_of_samples
    else:
        # If some date is missing, just set static window to one day.
        period = 3600 * 24
    return period


#TODO(lsmola) push this function to Horizon common then delete this
def _calc_date_args(date_from, date_to, date_options):
    # TODO(lsmola) all timestamps should probably work with
    # current timezone. And also show the current timezone in chart.
    if date_options == "other":
        try:
            if date_from:
                date_from = datetime.strptime(date_from,
                                              "%Y-%m-%d")
            else:
                # TODO(lsmola) there should be probably the date
                # of the first sample as default, so it correctly
                # counts the time window. Though I need ordering
                # and limit of samples to obtain that.
                pass
            if date_to:
                date_to = datetime.strptime(date_to,
                                            "%Y-%m-%d")
                # It return beginning of the day, I want the and of
                # the day, so i will add one day without a second.
                date_to = (date_to + timedelta(days=1) -
                           timedelta(seconds=1))
            else:
                date_to = timezone.now()
        except Exception:
            raise ValueError("The dates haven't been "
                             "recognized")
    else:
        try:
            date_from = timezone.now() - timedelta(days=float(date_options))
            date_to = timezone.now()
        except Exception:
            raise ValueError("The time delta must be an "
                             "integer representing days.")
    return date_from, date_to


def url_part(meter_name, barchart):
    d = {'meter': meter_name}
    if barchart:
        d['barchart'] = True
    return urlencode(d)


def get_meter_name(meter):
    return meter.replace('.', '_')


def get_meters(meters):
    return [(m, get_meter_name(m)) for m in meters]


def get_barchart_stats(series, unit):
    values = [point['y'] for point in series[0]['data']]
    average = sum(values) / len(values)
    used = values[-1]
    first_date = series[0]['data'][0]['x']
    last_date = series[0]['data'][-1]['x']
    tooltip_average = _('Average %(average)s %(unit)s<br> From: '
                        '%(first_date)s, to: %(last_date)s') % (
                            dict(average=average, unit=unit,
                                 first_date=first_date,
                                 last_date=last_date)
                        )
    return average, used, tooltip_average


def create_json_output(series, barchart, unit, date_from, date_to):
    start_datetime = end_datetime = ''
    if date_from:
        start_datetime = date_from.strftime("%Y-%m-%dT%H:%M:%S")
    if date_to:
        end_datetime = date_to.strftime("%Y-%m-%dT%H:%M:%S")

    settings = copy.deepcopy(SETTINGS)
    settings['settings']['xMin'] = start_datetime
    settings['settings']['xMax'] = end_datetime

    if series and barchart:
        average, used, tooltip_average = get_barchart_stats(series, unit)
        settings['settings']['yMin'] = 0
        settings['settings']['yMax'] = 100
        settings['stats']['average'] = average
        settings['stats']['used'] = used
        settings['stats']['tooltip_average'] = tooltip_average
    else:
        del settings['settings']['bar_chart_settings']
        del settings['stats']

    json_output = {'series': series}
    json_output = dict(json_output.items() + settings.items())
    return json_output


def handle_swap_util(series):
    # Divide available swap with used swap, multiply by 100.
    # Integers are good enough here.
    util = total = {}
    for serie in series:
        if serie['meter'] == 'hardware.memory.swap.util':
            util = serie.copy()
        else:
            total = serie.copy()

    for i, d in enumerate(util.get('data', [])):
        try:
            util['data'][i]['y'] =\
                int((100*d['y'])//total['data'][i]['y'])
        except IndexError:
            # Could happen if one series is shorter.
            del util['data'][i]
    util['unit'] = '%'
    return [util]
