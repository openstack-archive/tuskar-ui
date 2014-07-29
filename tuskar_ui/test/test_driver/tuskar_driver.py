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

from openstack_dashboard.test.test_data import utils

from tuskar_ui.test.test_data import tuskar_data

TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)

PLANS = []


class Plan:

    @classmethod
    def create(cls, name, description):
        global PLANS

        plan = TEST_DATA.tuskarclient_plans.first()
        PLANS.append(plan)
        return plan

    @classmethod
    def update(cls, plan_id, name, description):
        global PLANS

        plan = cls.get(plan_id)
        return plan

    @classmethod
    def list(cls):
        return PLANS

    @classmethod
    def get(cls, plan_id):
        for plan in PLANS:
            if plan['id'] == plan_id:
                return plan

    @classmethod
    def delete(cls, plan_id):
        global PLANS

        PLANS = [plan for plan in PLANS if plan['id'] != plan_id]
