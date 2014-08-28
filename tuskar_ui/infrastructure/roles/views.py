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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions as horizon_exceptions
from horizon import tables as horizon_tables
from horizon.utils import memoized

from tuskar_ui import api
from tuskar_ui.infrastructure.roles import tables


INDEX_URL = 'horizon:infrastructure:roles:index'


class OvercloudRoleMixin(object):
    @memoized.memoized
    def get_role(self, redirect=None):
        role_id = self.kwargs['role_id']
        role = api.tuskar.OvercloudRole.get(self.request, role_id,
                                            _error_redirect=redirect)
        return role


class StackMixin(object):
    @memoized.memoized
    def get_stack(self, redirect=None):
        if redirect is None:
            redirect = reverse(INDEX_URL)
        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        stack = api.heat.Stack.get_by_plan(self.request, plan)

        return stack


class IndexView(horizon_tables.DataTableView):
    table_class = tables.RolesTable
    template_name = "infrastructure/roles/index.html"

    def get_data(self):
        roles = api.tuskar.OvercloudRole.list(self.request)
        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        for role in roles:
            role_flavor = role.flavor(plan)
            role_image = role.image(plan)
            if role_flavor:
                role.flavor = role_flavor.name
            else:
                role.flavor = _('Unknown')
            if role_image:
                role.image = role_image.name
            else:
                role.image = _('Unknown')

        return roles


class DetailView(horizon_tables.DataTableView, OvercloudRoleMixin, StackMixin):
    table_class = tables.NodeTable
    template_name = 'infrastructure/roles/detail.html'

    @memoized.memoized
    def _get_nodes(self, stack, role):
        resources = stack.resources_by_role(role, with_joins=True)
        nodes = [r.node for r in resources]

        for node in nodes:
            # TODO(tzumainn): this could probably be done more efficiently
            # by getting the resource for all nodes at once
            try:
                resource = api.heat.Resource.get_by_node(self.request, node)
                node.role_name = resource.role.name
                node.role_id = resource.role.id
                node.stack_id = resource.stack.id
            except horizon_exceptions.NotFound:
                node.role_name = '-'

        return nodes

    def get_data(self):
        redirect = reverse(INDEX_URL)
        stack = self.get_stack(redirect)
        if stack:
            role = self.get_role(redirect)
            return self._get_nodes(stack, role)
        return []

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        redirect = reverse(INDEX_URL)

        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        stack = self.get_stack(redirect)
        role = self.get_role(redirect)

        context['role'] = role
        if stack:
            context['nodes'] = self._get_nodes(stack, role)
        else:
            context['nodes'] = []
        context['flavor'] = role.flavor(plan)
        # TODO(tzumainn): we don't mock images, so calling role.image(plan)
        # won't work right now
        context['image'] = role.image(plan)

        return context
