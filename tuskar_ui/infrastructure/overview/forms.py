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

import django.forms
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.forms
import horizon.messages

from tuskar_ui import api
import tuskar_ui.api.heat
import tuskar_ui.api.tuskar
import tuskar_ui.forms


def _get_role_count(plan, role):
    return plan.parameter_value(role.node_count_parameter_name, 0)


class EditPlan(horizon.forms.SelfHandlingForm):
    def __init__(self, *args, **kwargs):
        super(EditPlan, self).__init__(*args, **kwargs)
        self.plan = api.tuskar.Plan.get_the_plan(self.request)
        self.fields.update(self._role_count_fields(self.plan))

    def _role_count_fields(self, plan):
        fields = {}
        for role in plan.role_list:
            field = django.forms.IntegerField(
                label=role.name,
                widget=tuskar_ui.forms.NumberPickerInput,
                initial=_get_role_count(plan, role),
                # XXX Dirty hack for requiring a controller node.
                required=(role.name == 'Controller'),
            )
            fields['%s-count' % role.id] = field
        return fields

    def handle(self, request, data):
        # XXX Update the plan.
        return True


class DeployOvercloud(horizon.forms.SelfHandlingForm):
    def handle(self, request, data):
        try:
            plan = api.tuskar.Plan.get_the_plan(request)
            stack = api.heat.Stack.get_by_plan(self.request, plan)
            if not stack:
                api.heat.Stack.create(request,
                                      plan.name,
                                      plan.template,
                                      plan.parameters)
        except Exception:
            return False
        else:
            msg = _('Deployment in progress.')
            horizon.messages.success(request, msg)
            return True


class UndeployOvercloud(horizon.forms.SelfHandlingForm):
    def handle(self, request, data):
        try:
            plan = api.tuskar.Plan.get_the_plan(request)
            stack = api.heat.Stack.get_by_plan(self.request, plan)
            if stack:
                api.heat.Stack.delete(request, stack.id)
        except Exception:
            horizon.exceptions.handle(request,
                                      _("Unable to undeploy overcloud."))
            return False
        else:
            msg = _('Undeployment in progress.')
            horizon.messages.success(request, msg)
            return True
