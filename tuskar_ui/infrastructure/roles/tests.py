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
from openstack_dashboard.test.test_data import utils
from mock import patch, call  # noqa

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
UPDATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:roles:update', args=('role-1',))

TEST_DATA = utils.TestDataContainer()
flavor_data.data(TEST_DATA)
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)


class RolesTest(test.BaseAdminViewTests):

    def test_index_get(self):
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]
        plans = [api.tuskar.Plan(plan)
                 for plan in self.tuskarclient_plans.list()]
        flavor = self.novaclient_flavors.first()
        image = self.glanceclient_images.first()

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.list',
                  return_value=plans),
            patch('tuskar_ui.api.tuskar.Role.list',
                  return_value=roles),
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),
            patch('tuskar_ui.api.flavor.Flavor.get_by_name',
                  return_value=flavor)):
            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'infrastructure/roles/index.html')

    def test_detail_get(self):
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]
        plans = [api.tuskar.Plan(plan)
                 for plan in self.tuskarclient_plans.list()]
        flavor = self.novaclient_flavors.first()
        image = self.glanceclient_images.first()
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Role.list',
                  return_value=roles),
            patch('tuskar_ui.api.heat.Stack.get_by_plan',
                  return_value=stack),
            patch('tuskar_ui.api.heat.Stack.events',
                  return_value=[]),
            patch('tuskar_ui.api.heat.Stack.resources',
                  return_value=[]),
            patch('tuskar_ui.api.tuskar.Plan.list',
                  return_value=plans),
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),
            patch('tuskar_ui.api.flavor.Flavor.get_by_name',
                  return_value=flavor)):
            res = self.client.get(DETAIL_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/roles/detail.html')

    def test_update_get(self):
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]
        plans = [api.tuskar.Plan(plan)
                 for plan in self.tuskarclient_plans.list()]
        flavors = self.novaclient_flavors.list()
        images = self.glanceclient_images.list()
        stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Role.list',
                  return_value=roles),
            patch('tuskar_ui.api.heat.Stack.get_by_plan',
                  return_value=stack),
            patch('tuskar_ui.api.heat.Stack.events',
                  return_value=[]),
            patch('tuskar_ui.api.heat.Stack.resources',
                  return_value=[]),
            patch('tuskar_ui.api.tuskar.Plan.list',
                  return_value=plans),
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=images[0]),
            patch('tuskar_ui.api.flavor.Flavor.list',
                  return_value=flavors),
            patch('openstack_dashboard.api.glance.image_list_detailed',
                  return_value=[images])):

            res = self.client.get(UPDATE_URL)

            # Check that the expected fields are in the form:
            self.assertIn('id="id_flavor" name="flavor"', res.content)
            self.assertIn('id="id_image" name="image"', res.content)
            self.assertIn('flavor-1', res.content)
            self.assertIn('flavor-2', res.content)

    def test_update_post(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        role = api.tuskar.Role(self.tuskarclient_roles.first())
        flavors = self.novaclient_flavors.list()
        images = self.glanceclient_images.list()

        data = {
            'name': 'controller',
            'description': 'The controller node role.',
            'flavor': self.novaclient_flavors.first().name,
            'image': self.glanceclient_images.first().id,
            'nodes': '0',
        }

        with contextlib.nested(
            patch('tuskar_ui.api.flavor.Flavor.list',
                  return_value=flavors),
            patch('openstack_dashboard.api.glance.image_list_detailed',
                  return_value=[images]),
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=images[0]),
            patch('tuskar_ui.api.tuskar.Role.get',
                  return_value=role),
            patch('tuskar_ui.api.tuskar.Plan.patch',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                  return_value=plan)) as mocks:

            mock_patch = mocks[4]
            res = self.client.post(UPDATE_URL, data)
            self.assertRedirectsNoFollow(res, INDEX_URL)

            self.assertEqual(len(mock_patch.call_args_list), 1)
            args = mock_patch.call_args_list[0][0]
            self.assertEqual(args[1], plan.id)
            self.assertEqual(args[2]['Controller-1::Flavor'],  u'flavor-1')
            self.assertEqual(args[2]['Controller-1::Image'],  u'2')
