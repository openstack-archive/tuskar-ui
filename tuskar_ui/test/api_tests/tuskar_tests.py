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

from mock import patch  # noqa

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class TuskarAPITests(test.APITestCase):
    def test_plan_create(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.create',
                   return_value=plan):
            ret_val = api.tuskar.OvercloudPlan.create(self.request, {}, {})
        self.assertIsInstance(ret_val, api.tuskar.OvercloudPlan)

    def test_plan_list(self):
        plans = self.tuskarclient_plans.list()

        with patch('tuskarclient.v2.plans.PlanManager.list',
                   return_value=plans):
            ret_val = api.tuskar.OvercloudPlan.list(self.request)
        for plan in ret_val:
            self.assertIsInstance(plan, api.tuskar.OvercloudPlan)
        self.assertEqual(1, len(ret_val))

    def test_plan_get(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.get',
                   return_value=plan):
            ret_val = api.tuskar.OvercloudPlan.get(self.request, plan.id)

        self.assertIsInstance(ret_val, api.tuskar.OvercloudPlan)

    def test_plan_get_the_plan(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.list',
                   return_value=[plan]):
            with patch('tuskarclient.v2.plans.PlanManager.create',
                       return_value=plan):
                ret_val = api.tuskar.OvercloudPlan.get_the_plan(self.request)

        self.assertIsInstance(ret_val, api.tuskar.OvercloudPlan)

    def test_plan_delete(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.delete',
                   return_value=None):
            api.tuskar.OvercloudPlan.delete(self.request, plan.id)

    def test_plan_role_list(self):
        with patch('tuskarclient.v2.plans.PlanManager.get',
                   return_value=[]):
            plan = api.tuskar.OvercloudPlan(self.tuskarclient_plans.first(),
                                            self.request)

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=self.tuskarclient_roles.list()):
            ret_val = plan.role_list
        self.assertEqual(4, len(ret_val))
        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.OvercloudRole)

    def test_role_list(self):
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.OvercloudRole.list(self.request)

        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.OvercloudRole)
        self.assertEqual(4, len(ret_val))

    def test_role_get(self):
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.OvercloudRole.get(self.request,
                                                   roles[0].uuid)
        self.assertIsInstance(ret_val, api.tuskar.OvercloudRole)

    def test_role_get_by_image(self):
        plan = api.tuskar.OvercloudPlan(self.tuskarclient_plans.first())
        image = self.glanceclient_images.first()
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.OvercloudRole.get_by_image(
                self.request, plan, image)
        self.assertIsInstance(ret_val, api.tuskar.OvercloudRole)
        self.assertEqual(ret_val.name, 'Controller')
