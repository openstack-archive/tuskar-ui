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
        ret_val = api.tuskar.OvercloudPlan.create(self.request, {}, {})
        self.assertIsInstance(ret_val, api.tuskar.OvercloudPlan)

    def test_plan_list(self):
        ret_val = api.tuskar.OvercloudPlan.list(self.request)
        for plan in ret_val:
            self.assertIsInstance(plan, api.tuskar.OvercloudPlan)
        self.assertEqual(1, len(ret_val))

    def test_plan_get(self):
        plan = self.tuskarclient_plans.first()
        ret_val = api.tuskar.OvercloudPlan.get(self.request, plan['id'])

        self.assertIsInstance(ret_val, api.tuskar.OvercloudPlan)

    def test_plan_delete(self):
        plan = self.tuskarclient_plans.first()
        api.tuskar.OvercloudPlan.delete(self.request, plan['id'])

    def test_plan_role_list(self):
        plan = api.tuskar.OvercloudPlan(self.tuskarclient_plans.first())

        ret_val = plan.role_list

        self.assertEqual(4, len(ret_val))
        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.OvercloudRole)

    def test_role_list(self):
        ret_val = api.tuskar.OvercloudRole.list(self.request)

        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.OvercloudRole)
        self.assertEqual(5, len(ret_val))

    def test_role_get(self):
        role = self.tuskarclient_roles.first()
        ret_val = api.tuskar.OvercloudRole.get(self.request, role['id'])

        self.assertIsInstance(ret_val, api.tuskar.OvercloudRole)
