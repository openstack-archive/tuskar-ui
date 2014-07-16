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

from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import flavor_data
from tuskar_ui.test.test_data import heat_data
from tuskar_ui.test.test_data import node_data
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:manage_dashboard:index')

TEST_DATA = utils.TestDataContainer()
flavor_data.data(TEST_DATA)
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)


class OvercloudTests(test.BaseAdminViewTests):

    def test_index_no_plan_get(self):
        with contextlib.nested(
                patch('tuskar_ui.api.tuskar.OvercloudPlan.get_the_plan',
                      return_value=None),
        ):
            res = self.client.get(INDEX_URL)
            self.assertIn('<div class="span2 dashboard-item nodes done">',
                          res.content)
            self.assertIn('<div class="span2 dashboard-item flavors done">',
                          res.content)
            self.assertIn('<div class="span2 dashboard-item roles done">',
                          res.content)
            self.assertIn('<div class="span2 dashboard-item plans todo">',
                          res.content)
