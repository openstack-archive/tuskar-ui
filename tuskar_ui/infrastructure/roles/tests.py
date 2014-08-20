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
from tuskar_ui.test.test_data import flavor_data
from tuskar_ui.test.test_data import heat_data
from tuskar_ui.test.test_data import node_data
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:roles:index')
DETAIL_URL = urlresolvers.reverse(
    'horizon:infrastructure:roles:detail', args=('role-1',))

TEST_DATA = utils.TestDataContainer()
flavor_data.data(TEST_DATA)
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)


class RolesTest(test.BaseAdminViewTests):

    def test_index_get(self):
        roles = [api.tuskar.OvercloudRole(role)
                 for role in TEST_DATA.tuskarclient_roles.list()]
        flavor = TEST_DATA.novaclient_flavors.first()

        with contextlib.nested(
                patch('tuskar_ui.api.tuskar.OvercloudRole.list',
                      return_value=roles),
                patch('openstack_dashboard.api.nova.flavor_get',
                      return_value=flavor),
        ):
            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'infrastructure/roles/index.html')

    def test_detail_get(self):
        roles = [api.tuskar.OvercloudRole(role)
                 for role in TEST_DATA.tuskarclient_roles.list()]
        flavor = TEST_DATA.novaclient_flavors.first()

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': ['list', 'get'],
                'list.return_value': roles,
                'get.return_value': roles[0],
            }),
            patch('tuskar_ui.api.heat.Stack.events',
                  return_value=[]),
            patch('openstack_dashboard.api.nova.flavor_get',
                  return_value=flavor),
        ):
            res = self.client.get(DETAIL_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/roles/detail.html')
