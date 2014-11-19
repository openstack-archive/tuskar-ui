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

import json

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django import http
import django.utils.text
from django.utils.translation import ugettext_lazy as _
import heatclient
import horizon.forms
from horizon.utils import memoized

from tuskar_ui import api
from tuskar_ui.infrastructure.overview import forms


INDEX_URL = 'horizon:infrastructure:overview:index'


def _get_role_data(plan, stack, form, role):
    """Gathers data about a single deployment role.

    Gathers data about a single deployment role from the related Overcloud
    and Role objects, and presents it in the form convenient for use
    from the template.

    """
    data = {
        'id': role.id,
        'role': role,
        'name': role.name,
        'planned_node_count': plan.get_role_node_count(role),
        'field': form['%s-count' % role.id] if form else '',
    }

    if stack:
        resources = stack.resources(role=role, with_joins=True)
        nodes = [r.node for r in resources]
        node_count = len(nodes)

        deployed_node_count = 0
        deploying_node_count = 0
        error_node_count = 0
        waiting_node_count = node_count

        status = 'warning'
        if nodes:
            deployed_node_count = sum(1 for node in nodes
                                      if node.instance.status == 'ACTIVE')
            deploying_node_count = sum(1 for node in nodes
                                       if node.instance.status == 'BUILD')
            error_node_count = sum(1 for node in nodes
                                   if node.instance.status == 'ERROR')
            waiting_node_count = (node_count - deployed_node_count -
                                  deploying_node_count - error_node_count)
            if error_node_count:
                status = 'danger'
            elif deployed_node_count == data['planned_node_count']:
                status = 'success'
            else:
                status = 'info'

        finished = deployed_node_count == data['planned_node_count']
        if finished:
            icon = 'fa-check'
        elif status in ('danger', 'warning'):
            icon = 'fa-exclamation'
        else:
            icon = 'fa-spinner fa-spin'

        data.update({
            'status': status,
            'finished': finished,
            'total_node_count': node_count,
            'deployed_node_count': deployed_node_count,
            'deploying_node_count': deploying_node_count,
            'waiting_node_count': waiting_node_count,
            'error_node_count': error_node_count,
            'icon': icon,
        })

    # TODO(rdopieralski) get this from ceilometer
    # data['capacity'] = 20
    return data


class StackMixin(object):
    @memoized.memoized
    def get_stack(self):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        return api.heat.Stack.get_by_plan(self.request, plan)


class IndexView(horizon.forms.ModalFormView, StackMixin):
    template_name = 'infrastructure/overview/index.html'
    form_class = forms.EditPlan
    success_url = reverse_lazy(INDEX_URL)

    def get_progress_update(self, request, data):
        return {
            'progress': data.get('progress'),
            'show_last_events': data.get('show_last_events'),
            'last_events_title': unicode(data.get('last_events_title')),
            'last_events': [{
                'event_time': event.event_time,
                'resource_name': event.resource_name,
                'resource_status': event.resource_status,
                'resource_status_reason': event.resource_status_reason,
            } for event in data.get('last_events', [])],
            'roles': [{
                'status': role.get('status', 'warning'),
                'finished': role.get('finished', False),
                'name': role.get('name', ''),
                'slug': django.utils.text.slugify(role.get('name', '')),
                'id': role.get('id', ''),
                'total_node_count': role.get('node_count', 0),
                'deployed_node_count': role.get('deployed_node_count', 0),
                'deploying_node_count': role.get('deploying_node_count', 0),
                'waiting_node_count': role.get('waiting_node_count', 0),
                'error_node_count': role.get('error_node_count', 0),
                'planned_node_count': role.get('planned_node_count', 0),
                'icon': role.get('icon', ''),
            } for role in data.get('roles', [])],
        }

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_HORIZON_PROGRESS', ''):
            # If it's an AJAX call for progress update, send it.
            data = self.get_data(request, {})
            return http.HttpResponse(
                json.dumps(self.get_progress_update(request, data)),
                mimetype='application/json',
            )
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context.update(self.get_data(self.request, context))
        return context

    def get_data(self, request, context, *args, **kwargs):
        plan = api.tuskar.Plan.get_the_plan(request)
        stack = self.get_stack()
        form = context.get('form')

        context['plan'] = plan
        context['stack'] = stack

        roles = [_get_role_data(plan, stack, form, role)
                 for role in plan.role_list]
        context['roles'] = roles

        if stack:
            context['show_last_events'] = True
            failed_events = [e for e in stack.events
                             if 'FAILED' in e.resource_status and
                             'aborted' not in e.resource_status_reason][-3:]

            if failed_events:
                context['last_events_title'] = _('Last failed events')
                context['last_events'] = failed_events
            else:
                context['last_events_title'] = _('Last event')
                context['last_events'] = [stack.events[0]]

            if stack.is_deleting or stack.is_delete_failed:
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

                context['progress'] = min(95, max(
                    5, 100 * float(resources_count) / total_num_nodes_count))
            elif stack.is_deploying:
                total = sum(d['total_node_count'] for d in roles)
                context['progress'] = min(95, max(
                    5, 100 * sum(float(d.get('deployed_node_count', 0))
                                 for d in roles) / (total or 1)
                ))
            else:
                # stack is active
                if not stack.is_failed:
                    context['show_last_events'] = False
                context['progress'] = 100
                controller_role = plan.get_role_by_name("controller")
                context['admin_password'] = plan.parameter_value(
                    controller_role.parameter_prefix + 'AdminPassword')

                context['dashboard_urls'] = stack.dashboard_urls
        else:
            messages = forms.validate_plan(request, plan)
            context['plan_messages'] = messages
            context['plan_invalid'] = any(message.get('is_critical')
                                          for message in messages)
        return context

    def post(self, request, *args, **kwargs):
        """If the post comes from ajax, return validation results as json."""

        if not request.META.get('HTTP_X_HORIZON_VALIDATE', ''):
            return super(IndexView, self).post(request, *args, **kwargs)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            handled = form.handle(self.request, form.cleaned_data)
        else:
            handled = False
        if handled:
            messages = forms.validate_plan(request, form.plan)
        else:
            # TODO(rdopieralski) Actually iterate over the form errors and
            # add them all to the messages here.
            messages = [{
                'text': _(u"Error saving the plan."),
                'is_critical': True,
            }]
        # We need to unlazify all the lazy urls and translations.
        return http.HttpResponse(json.dumps({
            'plan_invalid': any(m.get('is_critical') for m in messages),
            'messages': [{
                'text': unicode(m.get('text', '')),
                'is_critical': m.get('is_critical', False),
                'link_url': unicode(m.get('link_url', '')),
                'link_label': unicode(m.get('link_label', '')),
            } for m in messages],
        }), mimetype='application/json')


class DeployConfirmationView(horizon.forms.ModalFormView, StackMixin):
    form_class = forms.DeployOvercloud
    template_name = 'infrastructure/overview/deploy_confirmation.html'
    submit_label = _("Deploy")

    def get_context_data(self, **kwargs):
        context = super(DeployConfirmationView,
                        self).get_context_data(**kwargs)
        plan = api.tuskar.Plan.get_the_plan(self.request)

        context['autogenerated_parameters'] = (
            plan.list_generated_parameters(with_prefix=False).keys())
        return context

    def get_success_url(self):
        return reverse(INDEX_URL)


class UndeployConfirmationView(horizon.forms.ModalFormView, StackMixin):
    form_class = forms.UndeployOvercloud
    template_name = 'infrastructure/overview/undeploy_confirmation.html'
    submit_label = _("Undeploy")

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


class PostDeployInitView(horizon.forms.ModalFormView, StackMixin):
    form_class = forms.PostDeployInit
    template_name = 'infrastructure/overview/post_deploy_init.html'
    submit_label = _("Initialize")

    def get_success_url(self):
        return reverse(INDEX_URL)

    def get_context_data(self, **kwargs):
        context = super(PostDeployInitView,
                        self).get_context_data(**kwargs)
        context['stack_id'] = self.get_stack().id
        return context

    def get_initial(self, **kwargs):
        initial = super(PostDeployInitView, self).get_initial(**kwargs)
        initial['stack_id'] = self.get_stack().id
        return initial


class ScaleOutView(horizon.forms.ModalFormView, StackMixin):
    form_class = forms.ScaleOut
    template_name = "infrastructure/overview/scale_out.html"
    submit_label = _("Deploy Changes")

    def get_success_url(self):
        return reverse(INDEX_URL)

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        context = super(ScaleOutView, self).get_context_data(*args, **kwargs)
        plan = api.tuskar.Plan.get_the_plan(self.request)
        form = context.get('form')
        roles = [_get_role_data(plan, None, form, role)
                 for role in plan.role_list]
        context.update({
            'roles': roles,
            'plan': plan,
        })
        return context
