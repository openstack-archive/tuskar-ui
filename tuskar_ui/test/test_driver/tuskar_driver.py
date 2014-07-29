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


class Plan:

    _plans = {}

    @classmethod
    def create(cls, name, description):
        plan = TEST_DATA.tuskarclient_plans.first()
        cls._plans[plan['id']] = plan
        return plan

    @classmethod
    def update(cls, plan_id, name, description):
        plan = cls.get(plan_id)
        # no updates for now
        return plan

    @classmethod
    def list(cls):
        return cls._plans.values()

    @classmethod
    def get(cls, plan_id):
        return cls._plans.get(plan_id, None)

    @classmethod
    def delete(cls, plan_id):
        cls._plans.pop(plan_id, None)
