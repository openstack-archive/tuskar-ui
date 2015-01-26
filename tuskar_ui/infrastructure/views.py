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

from horizon.utils import memoized

from tuskar_ui import api


class ItemCountMixin(object):
    def get_items_count(self):
        return len(self.get_data())

    def get_context_data(self, **kwargs):
        context = super(ItemCountMixin, self).get_context_data(**kwargs)
        context['items_count'] = self.get_items_count()
        return context


class StackMixin(object):
    @memoized.memoized
    def get_stack(self):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        return api.heat.Stack.get_by_plan(self.request, plan)


class RoleMixin(object):
    @memoized.memoized
    def get_role(self, redirect=None):
        role_id = self.kwargs['role_id']
        role = api.tuskar.Role.get(self.request, role_id,
                                   _error_redirect=redirect)
        return role
