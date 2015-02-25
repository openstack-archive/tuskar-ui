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
from tuskar_ui.infrastructure.overview import forms
from tuskar_ui.infrastructure.overview import views
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
            'list_generated_parameters',
            'make_generated_parameters',
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
        'list_generated_parameters.return_value': {},
        'make_generated_parameters.return_value': {},
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
                call(request, associated=False, maintenance=False),
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
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]

        with contextlib.nested(
                _mock_plan(**{'get_role_by_name.side_effect': None,
                              'get_role_by_name.return_value': roles[0]}),
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

        data = {
            'admin_email': "example@example.org",
            'public_host': '',
            'region': 'regionOne',
            'float_allocation_start': '10.0.0.2',
            'float_allocation_end': '10.255.255.254',
            'float_cidr': '10.0.0.0/8',
            'external_allocation_start': '192.0.2.45',
            'external_allocation_end': '192.0.2.64',
            'external_cidr': '192.0.2.0/24'
        }

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
                  return_value='keystone_client'),
            patch('os_cloud_config.utils.clients.get_neutron_client',
                  return_value='neutron_client'),
        ) as (mock_plan, mock_get_by_plan, mock_initialize,
              mock_setup_endpoints, mock_initialize_neutron,
              mock_get_keystone_client, mock_get_neutron_client):
            res = self.client.post(POST_DEPLOY_INIT_URL, data)

        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        mock_initialize.assert_called_once_with(
            '192.0.2.23', None, 'example@example.org', None, ssl=None,
            region='regionOne', user='heat-admin', public=None,
            pki_setup=False)
        mock_setup_endpoints.assert_called_once_with(
            {'nova': {'password': None},
             'heat': {'password': None},
             'ceilometer': {'password': None},
             'ec2': {'password': None},
             'horizon': {'port': ''},
             'cinder': {'password': None},
             'glance': {'password': None},
             'swift': {'password': None,
                       'path': '/v1/AUTH_%(tenant_id)s',
                       'admin_path': '/v1'},
             'novav3': {'password': None},
             'neutron': {'password': None}},
            os_auth_url=stack.keystone_auth_url,
            client='keystone_client',
            region='regionOne',
            public_host='')
        mock_initialize_neutron.assert_called_once_with(
            {'float':
                {'cidr': '10.0.0.0/8',
                 'allocation_start': '10.0.0.2',
                 'name': 'default-net',
                 'allocation_end': '10.255.255.254'},
             'external':
                {'cidr': '192.0.2.0/24',
                 'allocation_start': '192.0.2.45',
                 'name': 'ext-net',
                 'allocation_end': '192.0.2.64'}},
            keystone_client='keystone_client',
            neutron_client='neutron_client')
        mock_get_keystone_client.assert_called_once_with(
            'admin', None, 'admin', stack.keystone_auth_url)
        mock_get_neutron_client.assert_called_once_with(
            'admin', None, 'admin', stack.keystone_auth_url)

    def test_get_role_data(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        stack = api.heat.Stack(self.heatclient_stacks.first())
        role = api.tuskar.Role(self.tuskarclient_roles.first())
        stack.resources = lambda *args, **kwargs: []
        ret = views._get_role_data(plan, stack, None, role)
        self.assertEqual(ret, {
            'deployed_node_count': 0,
            'deploying_node_count': 0,
            'error_node_count': 0,
            'field': '',
            'finished': False,
            'icon': 'fa-exclamation',
            'id': 'role-1',
            'name': 'Controller',
            'planned_node_count': 1,
            'role': role,
            'status': 'warning',
            'total_node_count': 0,
            'waiting_node_count': 0,
        })

    def test_validate_plan_empty(self):
        with (
            _mock_plan()
        ) as plan, (
            patch('tuskar_ui.api.node.Node.list', return_value=[])
        ), (
            patch('tuskar_ui.api.flavor.Flavor.list', return_value=[])
        ):
            ret = forms.validate_plan(None, plan)
        for m in ret:
            m['text'] = unicode(m['text'])
        self.assertEqual(ret, [
            {
                'is_critical': True,
                'text': u'Define Flavors.',
                'status': 'pending',
                'classes': 'fa-square-o text-info',
            }, {
                'is_critical': True,
                'text': u'Register Nodes.',
                'status': 'pending',
                'classes': 'fa-square-o text-info',
            }, {
                'status': 'ok',
                'text': u'Configure Roles.',
                'classes': 'fa-check-square-o text-success',
            }, {
                'status': 'pending',
                'text': u'Assign roles.',
                'classes': 'fa-square-o text-info',
            }, {
                'is_critical': True,
                'text': u'Controller Role Needed.',
                'status': 'error',
                'indent': 1,
                'classes': 'fa-exclamation-circle text-danger',
            }, {
                'is_critical': True,
                'text': u'Compute Role Needed.',
                'status': 'error',
                'indent': 1,
                'classes': 'fa-exclamation-circle text-danger',
            },
        ])
