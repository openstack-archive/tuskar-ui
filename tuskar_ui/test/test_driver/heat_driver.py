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

from tuskar_ui.test.test_data import heat_data

TEST_DATA = utils.TestDataContainer()
heat_data.data(TEST_DATA)


class Stack:

    _stacks = {}

    @classmethod
    def create(cls, **kwargs):
        stack = TEST_DATA.heatclient_stacks.first()
        cls._stacks[stack.id] = stack
        return stack

    @classmethod
    def list(cls):
        return cls._stacks.values()

    @classmethod
    def get(cls, stack_id):
        return cls._stacks.get(stack_id, None)

    @classmethod
    def delete(cls, stack_id):
        cls._stacks.pop(stack_id, None)
