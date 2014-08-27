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


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:overview:index')
DEPLOY_URL = urlresolvers.reverse(
    'horizon:infrastructure:overview:deploy_confirmation')
DELETE_URL = urlresolvers.reverse(
    'horizon:infrastructure:overview:undeploy_confirmation')
POST_DEPLOY_INIT_URL = urlresolvers.reverse(
    'horizon:infrastructure:overview:post_deploy_init')
TEST_DATA = utils.TestDataContainer()
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
            'uuid',
            'patch',
            'parameters',
            'role_list',
            'parameter_value',
            'get_role_by_name',
            'get_role_node_count',
        ],
        'create.side_effect': lambda *args, **kwargs: plan,
        'delete.return_value': None,
        'get.side_effect': lambda *args, **kwargs: plan,
        'get_the_plan.side_effect': lambda *args, **kwargs: plan,
        'id': 'plan-1',
        'uuid': 'plan-1',
        'patch.side_effect': lambda *args, **kwargs: plan,
        'role_list': [],
        'parameter_value.return_value': None,
        'get_role_by_name.side_effect': KeyError,
        'get_role_node_count.return_value': 0,
    }
    params.update(kwargs)
    with patch(
            'tuskar_ui.api.tuskar.Plan', **params) as Plan:
        plan = Plan
        yield Plan


class OverviewTests(test.BaseAdminViewTests):

    def test_index_stack_not_created(self):
        with contextlib.nested(
            _mock_plan(),
            patch('tuskar_ui.api.heat.Stack.list', return_value=[]),
            patch('tuskar_ui.api.node.Node.list', return_value=[]),
            patch('tuskar_ui.api.flavor.Flavor.list', return_value=[]),
        ):
            res = self.client.get(INDEX_URL)
            get_the_plan = api.tuskar.Plan.get_the_plan
            request = get_the_plan.call_args_list[0][0][0]
            self.assertListEqual(get_the_plan.call_args_list, [
                call(request),
                call(request),
                call(request),
            ])
            self.assertListEqual(api.heat.Stack.list.call_args_list, [
                call(request),
            ])
            self.assertListEqual(api.node.Node.list.call_args_list, [
                call(request, associated=False),
            ])
            self.assertListEqual(api.flavor.Flavor.list.call_args_list, [
                call(request),
            ])
        self.assertTemplateUsed(
            res, 'infrastructure/overview/index.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overview/role_nodes_edit.html')

    def test_index_stack_not_created_post(self):
        with contextlib.nested(
            _mock_plan(),
            patch('tuskar_ui.api.heat.Stack.list', return_value=[]),
            patch('tuskar_ui.api.node.Node.list', return_value=[]),
            patch('tuskar_ui.api.flavor.Flavor.list', return_value=[]),
        ) as (plan, _stack_list, _node_list, _flavor_list):
            data = {
                'role-1-count': 1,
                'role-2-count': 0,
                'role-3-count': 0,
                'role-4-count': 0,
            }
            res = self.client.post(INDEX_URL, data)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            get_the_plan = api.tuskar.Plan.get_the_plan
            request = get_the_plan.call_args_list[0][0][0]
            self.assertListEqual(get_the_plan.call_args_list, [
                call(request),
            ])
            self.assertListEqual(
                api.tuskar.Plan.patch.call_args_list,
                [call(request, plan.id, {})],
            )

    def test_index_stack_deployed(self):
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.get_by_plan',
                      return_value=stack),
                patch('tuskar_ui.api.heat.Stack.events',
                      return_value=[]),
        ) as (Plan, stack_get_mock, stack_events_mock):
            res = self.client.get(INDEX_URL)
            request = Plan.get_the_plan.call_args_list[0][0][0]
            self.assertListEqual(
                Plan.get_the_plan.call_args_list,
                [
                    call(request),
                    call(request),
                    call(request),
                ])

        self.assertTemplateUsed(
            res, 'infrastructure/overview/index.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overview/deployment_live.html')

    def test_index_stack_undeploy_in_progress(self):
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.get_by_plan',
                      return_value=stack),
                patch('tuskar_ui.api.heat.Stack.is_deleting',
                      return_value=True),
                patch('tuskar_ui.api.heat.Stack.is_deployed',
                      return_value=False),
                patch('tuskar_ui.api.heat.Stack.resources',
                      return_value=[]),
                patch('tuskar_ui.api.heat.Stack.events',
                      return_value=[]),
        ):
            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/overview/index.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overview/deployment_progress.html')

    def test_deploy_get(self):
        with _mock_plan():
            res = self.client.get(DEPLOY_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/overview/deploy_confirmation.html')

    def test_delete_get(self):
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.get_by_plan',
                      return_value=stack),
        ):
            res = self.client.get(DELETE_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/overview/undeploy_confirmation.html')

    def test_delete_post(self):
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.get_by_plan',
                      return_value=stack),
                patch('tuskar_ui.api.heat.Stack.delete',
                      return_value=None),
        ):
            res = self.client.post(DELETE_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_post_deploy_init_get(self):
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
            _mock_plan(),
            patch('tuskar_ui.api.heat.Stack.get_by_plan',
                  return_value=stack),
        ):
            res = self.client.get(POST_DEPLOY_INIT_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/overview/post_deploy_init.html')

    def test_post_deploy_init_post(self):
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]

        with contextlib.nested(
            _mock_plan(**{'get_role_by_name.side_effect': None,
                          'get_role_by_name.return_value': roles[0]}),
            patch('tuskar_ui.api.heat.Stack.get_by_plan',
                  return_value=stack),
            patch('os_cloud_config.keystone.initialize',
                  return_value=None),
            patch('os_cloud_config.keystone.setup_endpoints',
                  return_value=None),
            patch('os_cloud_config.neutron.initialize_neutron',
                  return_value=None),
            patch('os_cloud_config.utils.clients.get_keystone_client',
                  return_value=None),
            patch('os_cloud_config.utils.clients.get_neutron_client',
                  return_value=None),
        ) as (mock_plan, mock_get_by_plan, mock_initialize,
              mock_setup_endpoints, mock_initialize_neutron,
              mock_get_keystone_client, mock_get_neutron_client):
            res = self.client.post(POST_DEPLOY_INIT_URL)

        self.assertRedirectsNoFollow(res, INDEX_URL)

        self.assertEqual(mock_initialize.call_count, 1)
        self.assertEqual(mock_setup_endpoints.call_count, 1)
        self.assertEqual(mock_initialize_neutron.call_count, 1)
        self.assertEqual(mock_get_keystone_client.call_count, 1)
        self.assertEqual(mock_get_neutron_client.call_count, 1)
