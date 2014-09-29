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
            ret_val = api.tuskar.Plan.create(self.request, {}, {})
        self.assertIsInstance(ret_val, api.tuskar.Plan)

    def test_plan_list(self):
        plans = self.tuskarclient_plans.list()

        with patch('tuskarclient.v2.plans.PlanManager.list',
                   return_value=plans):
            ret_val = api.tuskar.Plan.list(self.request)
        for plan in ret_val:
            self.assertIsInstance(plan, api.tuskar.Plan)
        self.assertEqual(1, len(ret_val))

    def test_plan_get(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.get',
                   return_value=plan):
            ret_val = api.tuskar.Plan.get(self.request, plan.uuid)

        self.assertIsInstance(ret_val, api.tuskar.Plan)

    def test_plan_get_the_plan(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.list',
                   return_value=[plan]):
            with patch('tuskarclient.v2.plans.PlanManager.create',
                       return_value=plan):
                ret_val = api.tuskar.Plan.get_the_plan(self.request)

        self.assertIsInstance(ret_val, api.tuskar.Plan)

    def test_plan_delete(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.delete',
                   return_value=None):
            api.tuskar.Plan.delete(self.request, plan.uuid)

    def test_plan_role_list(self):
        with patch('tuskarclient.v2.plans.PlanManager.get',
                   return_value=[]):
            plan = api.tuskar.Plan(self.tuskarclient_plans.first(),
                                   self.request)

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=self.tuskarclient_roles.list()):
            ret_val = plan.role_list
        self.assertEqual(4, len(ret_val))
        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.Role)

    def test_role_list(self):
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.Role.list(self.request)

        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.Role)
        self.assertEqual(4, len(ret_val))

    def test_role_get(self):
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.Role.get(self.request,
                                          roles[0].uuid)
        self.assertIsInstance(ret_val, api.tuskar.Role)

    def test_role_get_by_image(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        image = self.glanceclient_images.first()
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.Role.get_by_image(
                self.request, plan, image)
        self.assertIsInstance(ret_val, api.tuskar.Role)
        self.assertEqual(ret_val.name, 'Controller')

    def test_parameter_stripped_name(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        param = plan.parameter('Controller-1::count')

        ret_val = param.stripped_name
        self.assertEqual(ret_val, 'count')

    def test_parameter_role(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first(),
                               request=self.request)
        param = plan.parameter('Controller-1::count')
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = param.role
        self.assertIsInstance(ret_val, api.tuskar.Role)
        self.assertEqual(ret_val.name, 'Controller')
