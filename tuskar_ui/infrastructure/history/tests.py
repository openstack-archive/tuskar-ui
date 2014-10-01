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

from django.core import urlresolvers
from mock import patch, call  # noqa
from openstack_dashboard.test.test_data import utils

from tuskar_ui import api
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import heat_data
from tuskar_ui.test.test_data import tuskar_data


TEST_DATA = utils.TestDataContainer()
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)
INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:history:index')


class HistoryTest(test.BaseAdminViewTests):

    def test_index(self):
        plan = api.tuskar.Plan(
            TEST_DATA.tuskarclient_plans.first())
        stack = api.heat.Stack(
            TEST_DATA.heatclient_stacks.first())
        events = TEST_DATA.heatclient_events.list()

        with contextlib.nested(
                patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                      return_value=plan),
                patch('tuskar_ui.api.heat.Stack.get_by_plan',
                      return_value=stack),
                patch('tuskar_ui.api.heat.Stack.events',
                      return_value=events)
        ):
            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'infrastructure/history/index.html')
