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
    'horizon:infrastructure:overview:index')
DETAIL_URL = urlresolvers.reverse(
    'horizon:infrastructure:overview:detail', args=('stack-id-1',))
UNDEPLOY_IN_PROGRESS_URL = urlresolvers.reverse(
    'horizon:infrastructure:overview:undeploy_in_progress',
    args=('overcloud',))
DETAIL_URL_CONFIGURATION_TAB = (DETAIL_URL +
                                "?tab=detail__configuration")
DELETE_URL = urlresolvers.reverse(
    'horizon:infrastructure:overview:undeploy_confirmation',
    args=('stack-id-1',))
PLAN_CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:plans:create')
TEST_DATA = utils.TestDataContainer()
flavor_data.data(TEST_DATA)
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)


@contextlib.contextmanager
def _mock_plan(**kwargs):
    plan = None

    params = {
        'spec_set': [
            'create',
            'delete',
            'get',
            'get_the_plan',
            'id',
            'update',
            'parameters',
            'role_list',
        ],
        'create.side_effect': lambda *args, **kwargs: plan,
        'delete.return_value': None,
        'get.side_effect': lambda *args, **kwargs: plan,
        'get_the_plan.side_effect': lambda *args, **kwargs: plan,
        'id': 1,
        'update.side_effect': lambda *args, **kwargs: plan,
        'role_list': [],
    }
    params.update(kwargs)
    with patch(
            'tuskar_ui.api.tuskar.OvercloudPlan', **params) as OvercloudPlan:
        plan = OvercloudPlan
        yield OvercloudPlan


class OvercloudTests(test.BaseAdminViewTests):

    def test_index_overcloud_undeployed_get(self):
        with _mock_plan(**{'get_the_plan.side_effect': None,
                           'get_the_plan.return_value': None}):
            res = self.client.get(INDEX_URL)

        self.assertRedirectsNoFollow(res, PLAN_CREATE_URL)

    def test_index_overcloud_deployed_stack_not_created(self):
        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.is_deployed',
                      return_value=False),
        ):
            res = self.client.get(INDEX_URL)
            request = api.tuskar.OvercloudPlan.get_the_plan. \
                call_args_list[0][0][0]
            self.assertListEqual(
                api.tuskar.OvercloudPlan.get_the_plan.call_args_list,
                [call(request)])
        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_index_overcloud_deployed(self):
        with _mock_plan() as OvercloudPlan:
            res = self.client.get(INDEX_URL)
            request = OvercloudPlan.get_the_plan.call_args_list[0][0][0]
            self.assertListEqual(OvercloudPlan.get_the_plan.call_args_list,
                                 [call(request)])

        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_detail_get(self):
        roles = [api.tuskar.OvercloudRole(role)
                 for role in TEST_DATA.tuskarclient_roles.list()]

        with contextlib.nested(
            _mock_plan(),
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            patch('tuskar_ui.api.heat.Stack.events',
                  return_value=[]),
        ):
            res = self.client.get(DETAIL_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/overview/detail.html')
        self.assertTemplateNotUsed(
            res, 'horizon/common/_detail_table.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overview/_detail_overview.html')

    def test_detail_get_configuration_tab(self):
        with _mock_plan():
            res = self.client.get(DETAIL_URL_CONFIGURATION_TAB)

        self.assertTemplateUsed(
            res, 'infrastructure/overview/detail.html')
        self.assertTemplateNotUsed(
            res, 'infrastructure/overview/_detail_overview.html')
        self.assertTemplateUsed(
            res, 'horizon/common/_detail_table.html')

    def test_delete_get(self):
        res = self.client.get(DELETE_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/overview/undeploy_confirmation.html')

    def test_delete_post(self):
        with _mock_plan():
            res = self.client.post(DELETE_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_undeploy_in_progress(self):
        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.is_deleting',
                      return_value=True),
                patch('tuskar_ui.api.heat.Stack.is_deployed',
                      return_value=False),
                patch('tuskar_ui.api.heat.Stack.events',
                      return_value=[]),
        ):
            res = self.client.get(UNDEPLOY_IN_PROGRESS_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/overview/detail.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overview/_undeploy_in_progress.html')
        self.assertTemplateNotUsed(
            res, 'horizon/common/_detail_table.html')

    def test_undeploy_in_progress_finished(self):
        with _mock_plan(**{'get_the_plan.side_effect': None,
                           'get_the_plan.return_value': None}):
            res = self.client.get(UNDEPLOY_IN_PROGRESS_URL)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_undeploy_in_progress_invalid(self):
        with _mock_plan():
            res = self.client.get(UNDEPLOY_IN_PROGRESS_URL)

        self.assertRedirectsNoFollow(res, DETAIL_URL)
