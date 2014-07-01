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
from django.views.generic import base as base_views

from horizon import exceptions as horizon_exceptions
import horizon.forms
from horizon import messages
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs
from horizon.utils import memoized

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import forms
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui.infrastructure.overcloud import tabs


INDEX_URL = 'horizon:infrastructure:overcloud:index'
DETAIL_URL = 'horizon:infrastructure:overcloud:detail'
PLAN_CREATE_URL = 'horizon:infrastructure:plans:create'
UNDEPLOY_IN_PROGRESS_URL = (
    'horizon:infrastructure:overcloud:undeploy_in_progress')


class StackMixin(object):
    @memoized.memoized
    def get_stack(self, redirect=None):
        if redirect is None:
            redirect = reverse(INDEX_URL)
        stack_id = self.kwargs['stack_id']
        stack = api.heat.Stack.get(self.request, stack_id,
                                   _error_redirect=redirect)
        return stack


class OvercloudRoleMixin(object):
    @memoized.memoized
    def get_role(self, redirect=None):
        role_id = self.kwargs['role_id']
        role = api.tuskar.OvercloudRole.get(self.request, role_id,
                                            _error_redirect=redirect)
        return role


class IndexView(base_views.RedirectView):
    permanent = False

    def get_redirect_url(self):
        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)

        redirect = reverse(PLAN_CREATE_URL)
        if plan is not None:
            stacks = api.heat.Stack.list(self.request)
            for stack in stacks:
                if stack.plan.id == plan.id:
                    break
            else:
                stack = None

            if stack is not None:
                if stack.is_deleting or stack.is_delete_failed:
                    redirect = reverse(UNDEPLOY_IN_PROGRESS_URL,
                                       args=(stack.id,))
                else:
                    redirect = reverse(DETAIL_URL,
                                       args=(stack.id,))
        return redirect


class DetailView(horizon_tabs.TabView, StackMixin):
    tab_group_class = tabs.DetailTabs
    template_name = 'infrastructure/overcloud/detail.html'

    def get_tabs(self, request, **kwargs):
        stack = self.get_stack()
        return self.tab_group_class(request, stack=stack, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['stack'] = self.get_stack()
        context['plan'] = self.get_stack().plan
        return context


class UndeployConfirmationView(horizon.forms.ModalFormView):
    form_class = forms.UndeployOvercloud
    template_name = 'infrastructure/overcloud/undeploy_confirmation.html'

    def get_success_url(self):
        return reverse(INDEX_URL)

    def get_context_data(self, **kwargs):
        context = super(UndeployConfirmationView,
                        self).get_context_data(**kwargs)
        context['stack_id'] = self.kwargs['stack_id']
        return context

    def get_initial(self, **kwargs):
        initial = super(UndeployConfirmationView, self).get_initial(**kwargs)
        initial['stack_id'] = self.kwargs['stack_id']
        return initial


class UndeployInProgressView(horizon_tabs.TabView, StackMixin, ):
    tab_group_class = tabs.UndeployInProgressTabs
    template_name = 'infrastructure/overcloud/detail.html'

    def get_stack_or_redirect(self):
        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        stack = None

        if plan is not None:
            stack = None
            stacks = api.heat.Stack.list(self.request)
            for s in stacks:
                if s.plan.id == plan.id:
                    stack = s
                    break

        if stack is None:
            redirect = reverse(INDEX_URL)
            messages.success(self.request,
                             _("Undeploying of the Overcloud has finished."))
            raise horizon_exceptions.Http302(redirect)
        elif stack.is_deleting or stack.is_delete_failed:
            return stack
        else:
            messages.error(self.request,
                           _("Overcloud is not being undeployed."))
            redirect = reverse(DETAIL_URL,
                               args=(stack.id,))
            raise horizon_exceptions.Http302(redirect)

    def get_tabs(self, request, **kwargs):
        stack = self.get_stack_or_redirect()
        return self.tab_group_class(request, stack=stack, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UndeployInProgressView,
                        self).get_context_data(**kwargs)
        context['stack'] = self.get_stack_or_redirect()
        return context


class OvercloudRoleView(horizon_tables.DataTableView,
                        OvercloudRoleMixin, StackMixin):
    table_class = tables.OvercloudRoleNodeTable
    template_name = 'infrastructure/overcloud/overcloud_role.html'

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
            except horizon_exceptions.NotFound:
                node.role_name = '-'

        return nodes

    def get_data(self):
        stack = self.get_stack()
        redirect = reverse(DETAIL_URL,
                           args=(stack.id,))
        role = self.get_role(redirect)
        return self._get_nodes(stack, role)

    def get_context_data(self, **kwargs):
        context = super(OvercloudRoleView, self).get_context_data(**kwargs)

        stack = self.get_stack()
        redirect = reverse(DETAIL_URL,
                           args=(stack.id,))
        role = self.get_role(redirect)
        context['role'] = role
        # TODO(tzumainn) we need to do this from plan parameters
        context['image_name'] = 'FIXME'
        context['nodes'] = self._get_nodes(stack, role)
        context['flavor'] = None

        return context
