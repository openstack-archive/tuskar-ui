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
from novaclient import exceptions as nova_exceptions
from novaclient.v1_1 import servers
from openstack_dashboard.test.test_data import utils

from tuskar_ui import api
from tuskar_ui.infrastructure.flavors import utils as flavors_utils
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import flavor_data
from tuskar_ui.test.test_data import heat_data
from tuskar_ui.test.test_data import tuskar_data


TEST_DATA = utils.TestDataContainer()
flavor_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)
INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:flavors:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:flavors:create')
DETAILS_VIEW = 'horizon:infrastructure:flavors:details'


@contextlib.contextmanager
def _prepare_create():
    flavor = TEST_DATA.novaclient_flavors.first()
    all_flavors = TEST_DATA.novaclient_flavors.list()
    data = {'name': 'foobar',
            'vcpus': 3,
            'memory_mb': 1024,
            'disk_gb': 40,
            'arch': 'amd64'}
    with contextlib.nested(
            patch('tuskar_ui.api.flavor.Flavor.create',
                  return_value=flavor),
            # Inherited code calls this directly
            patch('openstack_dashboard.api.nova.flavor_list',
                  return_value=all_flavors),
    ) as mocks:
            yield mocks[0], data


def _raise_nova_client_exception(*args, **kwargs):
    raise nova_exceptions.ClientException("Boom!")


class FlavorsTest(test.BaseAdminViewTests):

    def test_index(self):
        plans = [api.tuskar.Plan(plan, self.request)
                 for plan in TEST_DATA.tuskarclient_plans.list()]
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]

        with contextlib.nested(
                patch('tuskar_ui.api.tuskar.Plan.list',
                      return_value=plans),
                patch('tuskar_ui.api.tuskar.Role.list',
                      return_value=roles),
                patch('openstack_dashboard.api.nova.flavor_list',
                      return_value=TEST_DATA.novaclient_flavors.list()),
                patch('openstack_dashboard.api.nova.server_list',
                      return_value=([], False)),
        ) as (plans_mock, roles_mock, flavors_mock, servers_mock):
            res = self.client.get(INDEX_URL)
            self.assertEqual(plans_mock.call_count, 1)
            self.assertEqual(roles_mock.call_count, 4)
            self.assertEqual(flavors_mock.call_count, 3)
            self.assertEqual(servers_mock.call_count, 1)

        self.assertTemplateUsed(res, 'infrastructure/flavors/index.html')

    def test_index_recoverable_failure(self):
        with patch('openstack_dashboard.api.nova.flavor_list',
                   side_effect=_raise_nova_client_exception) as flavor_list:
            res = self.client.get(INDEX_URL)
            self.assertEqual(flavor_list.call_count, 2)
        self.assertEqual(
            [(m.message, m.tags) for m in res.context['messages']],
            [
                (u'Unable to retrieve flavor list.', u'error'),
                (u'Unable to retrieve nodes', u'error'),
            ],
        )
        self.assertMessageCount(response=res, error=2, warning=0)

    def test_create_get(self):
        res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(res, 'infrastructure/flavors/create.html')

    def test_create_post_ok(self):
        with _prepare_create() as (create_mock, data):
            res = self.client.post(CREATE_URL, data)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            request = create_mock.call_args_list[0][0][0]
            self.assertListEqual(create_mock.call_args_list, [
                call(request, name=u'foobar', memory=1024, vcpus=3, disk=40,
                     cpu_arch='amd64')
            ])

    def test_create_post_name_exists(self):
        flavor = TEST_DATA.novaclient_flavors.first()
        with _prepare_create() as (create_mock, data):
            data['name'] = flavor.name
            res = self.client.post(CREATE_URL, data)
            self.assertFormErrors(res)

    def test_delete_ok(self):
        flavors = TEST_DATA.novaclient_flavors.list()
        data = {'action': 'flavors__delete',
                'object_ids': [flavors[0].id, flavors[1].id]}
        with contextlib.nested(
                patch('openstack_dashboard.api.nova.flavor_delete'),
                patch('openstack_dashboard.api.nova.server_list',
                      return_value=([], False)),
                patch('tuskar_ui.api.tuskar.Role.list',
                      return_value=[]),
                patch('tuskar_ui.api.tuskar.Plan.list',
                      return_value=[]),
                patch('openstack_dashboard.api.nova.flavor_list',
                      return_value=TEST_DATA.novaclient_flavors.list())
        ):
            res = self.client.post(INDEX_URL, data)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_deployed_on_servers(self):
        flavors = TEST_DATA.novaclient_flavors.list()
        server = servers.Server(
            servers.ServerManager(None),
            {'id': 'aa',
             'name': 'Compute',
             'image': {'id': 1},
             'status': 'ACTIVE',
             'flavor': {'id': flavors[0].id}}
        )
        data = {'action': 'flavors__delete',
                'object_ids': [flavors[0].id, flavors[1].id]}
        with contextlib.nested(
                patch('openstack_dashboard.api.nova.flavor_delete'),
                patch('openstack_dashboard.api.nova.server_list',
                      return_value=([server], False)),
                patch('tuskar_ui.api.tuskar.Role.list',
                      return_value=[]),
                patch('tuskar_ui.api.tuskar.Plan.list',
                      return_value=[]),
                patch('openstack_dashboard.api.nova.flavor_list',
                      return_value=TEST_DATA.novaclient_flavors.list()),
                patch('tuskar_ui.api.node.Node.list',
                      return_value=[])
        ):
            res = self.client.post(INDEX_URL, data)
            self.assertMessageCount(error=1, warning=0)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_details_no_overcloud(self):
        flavor = api.flavor.Flavor(TEST_DATA.novaclient_flavors.first())
        plan = api.tuskar.Plan(TEST_DATA.tuskarclient_plans.first())
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]

        with contextlib.nested(
                patch('tuskar_ui.api.flavor.Flavor.get',
                      return_value=flavor),
                patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                      return_value=plan),
                patch('tuskar_ui.api.tuskar.Role.list', return_value=roles),
                patch('tuskar_ui.api.tuskar.Role.flavor', return_value=flavor),
        ) as (get_mock, plan_mock, roles_mock, role_flavor_mock):
            res = self.client.get(urlresolvers.reverse(DETAILS_VIEW,
                                                       args=(flavor.id,)))
            self.assertEqual(get_mock.call_count, 1)
            self.assertEqual(plan_mock.call_count, 2)
            self.assertEqual(roles_mock.call_count, 1)
            self.assertEqual(role_flavor_mock.call_count, 4)
        self.assertTemplateUsed(res, 'infrastructure/flavors/details.html')

    def test_details(self):
        flavor = api.flavor.Flavor(TEST_DATA.novaclient_flavors.first())
        plan = api.tuskar.Plan(TEST_DATA.tuskarclient_plans.first())
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
                patch('tuskar_ui.api.flavor.Flavor.get',
                      return_value=flavor),
                patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                      return_value=plan),
                patch('tuskar_ui.api.tuskar.Role.list', return_value=roles),
                patch('tuskar_ui.api.tuskar.Role.flavor', return_value=flavor),
                patch('tuskar_ui.api.heat.Stack.get_by_plan',
                      return_value=stack),
                # __name__ is required for horizon.tables
                patch('tuskar_ui.api.heat.Stack.resources_count',
                      return_value=42, __name__='')
        ) as (flavor_mock, plan_mock, roles_mock, role_flavor_mock,
              stack_mock, count_mock):
            res = self.client.get(urlresolvers.reverse(DETAILS_VIEW,
                                                       args=(flavor.id,)))
            self.assertEqual(flavor_mock.call_count, 1)
            self.assertEqual(plan_mock.call_count, 2)
            self.assertEqual(roles_mock.call_count, 1)
            self.assertEqual(role_flavor_mock.call_count, 4)
            self.assertEqual(stack_mock.call_count, 1)
            self.assertEqual(count_mock.call_count, 4)
        self.assertTemplateUsed(res, 'infrastructure/flavors/details.html')


class FlavorsUtilsTest(test.TestCase):
    def test_get_unmached_suggestions(self):
        flavors = [api.flavor.Flavor(flavor)
                   for flavor in TEST_DATA.novaclient_flavors.list()]
        nodes = [api.node.Node(api.node.IronicNode(node))
                 for node in self.ironicclient_nodes.list()]
        with (
            patch('tuskar_ui.api.flavor.Flavor.list', return_value=flavors)
        ), (
            patch('tuskar_ui.api.node.Node.list', return_value=nodes)
        ):
            ret = flavors_utils.get_flavor_suggestions(None)
        FS = flavors_utils.FlavorSuggestion
        self.assertEqual(ret, set([
            FS(vcpus=8, ram_bytes=4294967296, disk_bytes=10737418240,
               cpu_arch='x86_64', node_id='aa-11'),
            FS(vcpus=16, ram_bytes=4294967296, disk_bytes=107374182400,
               cpu_arch='x86_64', node_id='bb-22'),
            FS(vcpus=32, ram_bytes=8589934592, disk_bytes=1073741824,
               cpu_arch='x86_64', node_id='cc-33'),
            FS(vcpus=8, ram_bytes=4294967296, disk_bytes=10737418240,
               cpu_arch='x86_64', node_id='cc-44'),
            FS(vcpus=8, ram_bytes=4294967296, disk_bytes=10737418240,
               cpu_arch='x86_64', node_id='dd-55'),
            FS(vcpus=8, ram_bytes=4294967296, disk_bytes=10737418240,
               cpu_arch='x86_64', node_id='ff-66'),
            FS(vcpus=8, ram_bytes=4294967296, disk_bytes=10737418240,
               cpu_arch='x86_64', node_id='gg-77'),
            FS(vcpus=8, ram_bytes=4294967296, disk_bytes=10737418240,
               cpu_arch='x86_64', node_id='hh-88'),
            FS(vcpus=16, ram_bytes=8589934592, disk_bytes=1073741824000,
               cpu_arch='x86_64', node_id='ii-99'),
        ]))
