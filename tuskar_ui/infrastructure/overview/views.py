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

import heatclient

import horizon.forms
from horizon.utils import memoized
from horizon import views as horizon_views

from tuskar_ui import api
from tuskar_ui.infrastructure.overview import forms


INDEX_URL = 'horizon:infrastructure:overview:index'


def _get_role_data(plan, stack, role):
    """Gathers data about a single deployment role from the related Overcloud
    and OvercloudRole objects, and presents it in the form convenient for use
    from the template.

    """
    data = {
        'role': role,
        'name': role.name,
        'planned_node_count': plan.parameter_value(
            role.node_count_parameter_name, 0)
    }

    if stack:
        resources = stack.resources_by_role(role, with_joins=True)
        nodes = [r.node for r in resources]
        node_count = len(nodes)

        deployed_node_count = 0
        deploying_node_count = 0
        error_node_count = 0
        waiting_node_count = node_count

        if nodes:
            deployed_node_count = sum(1 for node in nodes
                                      if node.instance.status == 'ACTIVE')
            deploying_node_count = sum(1 for node in nodes
                                       if node.instance.status == 'BUILD')
            error_node_count = sum(1 for node in nodes
                                   if node.instance.status == 'ERROR')
            waiting_node_count = (node_count - deployed_node_count -
                                  deploying_node_count - error_node_count)
        data.update({
            'total_node_count': node_count,
            'deployed_node_count': deployed_node_count,
            'deploying_node_count': deploying_node_count,
            'waiting_node_count': waiting_node_count,
            'error_node_count': error_node_count,
        })

    # TODO(rdopieralski) get this from ceilometer
    # data['capacity'] = 20
    return data


class StackMixin(object):
    @memoized.memoized
    def get_stack(self, redirect=None):
        if redirect is None:
            redirect = reverse(INDEX_URL)
        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        stack = api.heat.Stack.get_by_plan(self.request, plan)

        return stack


class IndexView(horizon_views.APIView, StackMixin):
    template_name = 'infrastructure/overview/index.html'

    def get_data(self, request, context, *args, **kwargs):
        plan = api.tuskar.OvercloudPlan.get_the_plan(request)
        stack = self.get_stack()

        context['plan'] = plan
        context['stack'] = stack

        roles = [_get_role_data(plan, stack, role)
                 for role in plan.role_list]
        context['roles'] = roles

        if stack:
            context['last_failed_events'] = [
                e for e in stack.events
                if e.resource_status == 'DELETE_FAILED'][-3:]

            if stack.is_deleting or stack.is_delete_failed:
                # stack is being deleted

                # TODO(lsmola) since at this point we don't have total number
                # of nodes we will hack this around, till API can show this
                # information. So it will actually show progress like the total
                # number is 10, or it will show progress of 5%. Ugly, but
                # workable.
                total_num_nodes_count = 10

                try:
                    resources_count = len(
                        stack.resources(with_joins=False))
                except heatclient.exc.HTTPNotFound:
                    # Immediately after undeploying has started, heat returns
                    # this exception so we can take it as kind of init of
                    # undeploying.
                    resources_count = total_num_nodes_count

                # TODO(lsmola) same as hack above
                total_num_nodes_count = max(
                    resources_count, total_num_nodes_count)

                context['progress'] = max(
                    5, 100 * (total_num_nodes_count - resources_count))
            else:
                # stack is active
                total = sum(d['total_node_count'] for d in roles)
                context['progress'] = 100 * sum(d.get('deployed_node_count', 0)
                                                for d in roles) // (total or 1)
                context['dashboard_urls'] = stack.dashboard_urls

        return context


class DeployConfirmationView(horizon.forms.ModalFormView, StackMixin):
    form_class = forms.DeployOvercloud
    template_name = 'infrastructure/overview/deploy_confirmation.html'

    def get_success_url(self):
        return reverse(INDEX_URL)


class UndeployConfirmationView(horizon.forms.ModalFormView, StackMixin):
    form_class = forms.UndeployOvercloud
    template_name = 'infrastructure/overview/undeploy_confirmation.html'

    def get_success_url(self):
        return reverse(INDEX_URL)

    def get_context_data(self, **kwargs):
        context = super(UndeployConfirmationView,
                        self).get_context_data(**kwargs)
        context['stack_id'] = self.get_stack().id
        return context

    def get_initial(self, **kwargs):
        initial = super(UndeployConfirmationView, self).get_initial(**kwargs)
        initial['stack_id'] = self.get_stack().id
        return initial
