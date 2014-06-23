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

from __future__ import absolute_import

import contextlib
from mock import patch  # noqa

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class TuskarAPITests(test.APITestCase):
    def test_overcloud_plan_create(self):
        plan = self.tuskarclient_overcloud_plans.first()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.create',
                   return_value=plan):
            ret_val = api.tuskar.OvercloudPlan.create(self.request, {}, {})
        self.assertIsInstance(ret_val, api.tuskar.OvercloudPlan)

    def test_overcloud_plan_list(self):
        plans = self.tuskarclient_overcloud_plans.list()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.list',
                   return_value=plans):
            ret_val = api.tuskar.OvercloudPlan.list(self.request)
        for plan in ret_val:
            self.assertIsInstance(plan, api.tuskar.OvercloudPlan)
        self.assertEqual(1, len(ret_val))

    def test_overcloud_plan_get(self):
        plan = self.tuskarclient_overcloud_plans.first()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.list',
                   return_value=[plan]):
            ret_val = api.tuskar.OvercloudPlan.get(self.request, plan.id)

        self.assertIsInstance(ret_val, api.tuskar.OvercloudPlan)

    def test_overcloud_plan_delete(self):
        plan = self.tuskarclient_overcloud_plans.first()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.delete',
                   return_value=None):
            api.tuskar.OvercloudPlan.delete(self.request, plan.id)

    def test_overcloud_role_list(self):
        roles = self.tuskarclient_overcloud_roles.list()

        with patch('tuskarclient.v1.overcloud_roles.OvercloudRoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.OvercloudRole.list(self.request)

        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.OvercloudRole)
        self.assertEqual(4, len(ret_val))

    def test_overcloud_role_get(self):
        role = self.tuskarclient_overcloud_roles.first()

        with patch('tuskarclient.v1.overcloud_roles.OvercloudRoleManager.get',
                   return_value=role):
            ret_val = api.tuskar.OvercloudRole.get(self.request, role.id)

        self.assertIsInstance(ret_val, api.tuskar.OvercloudRole)

    def test_overcloud_role_get_by_node(self):
        node = api.node.Node(
            api.node.BareMetalNode(self.baremetalclient_nodes.first()))
        instance = self.novaclient_servers.first()
        image = self.glanceclient_images.first()
        roles = self.tuskarclient_overcloud_roles.list()

        with contextlib.nested(
                patch('tuskarclient.v1.overcloud_roles.'
                      'OvercloudRoleManager.list',
                      return_value=roles),
                patch('openstack_dashboard.api.nova.server_get',
                      return_value=instance),
                patch('openstack_dashboard.api.glance.image_get',
                      return_value=image),
        ):
            ret_val = api.tuskar.OvercloudRole.get_by_node(self.request,
                                                           node)
        self.assertEqual(ret_val.name, 'Controller')
