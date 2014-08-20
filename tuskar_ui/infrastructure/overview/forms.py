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
from os_cloud_config import keystone as keystone_setup

from tuskar_ui import api
import tuskar_ui.forms


def _get_role_count(plan, role):
    return plan.parameter_value(role.node_count_parameter_name, 0)


class EditPlan(horizon.forms.SelfHandlingForm):
    def __init__(self, *args, **kwargs):
        super(EditPlan, self).__init__(*args, **kwargs)
        self.plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
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
            plan = api.tuskar.OvercloudPlan.get_the_plan(request)
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
            plan = api.tuskar.OvercloudPlan.get_the_plan(request)
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


class PostDeployInit(horizon.forms.SelfHandlingForm):
    def build_endpoints(self, plan):
        # TODO(lsmola) add passwords from the plan
        return {
            "ceilometer": {"password": ''},
            "cinder": {"password": ''},
            "ec2": {"password": ''},
            "glance": {"password": '16b4aaa3e056d07f796a93afb6010487b7b617e7'},
            "heat": {"password": ''},
            "neutron": {"password": ''},
            "nova": {"password": ''},
            "novav3": {"password": ''},
            "swift": {"password": ''},
            "horizon": {}}

    def handle(self, request, data):
        try:
            plan = api.tuskar.OvercloudPlan.get_the_plan(request)
            stack = api.heat.Stack.get_by_plan(self.request, plan)

            # TODO(lsmola) replace by data from TuskarAPI once available
            admin_token = 'aa61677c0a270880e99293c148cefee4000b2259'
            admin_password = '5ba3a69c95c668daf84c2f103ebec82d273a4897'
            admin_email = 'example@example.org'
            auth_ip = stack.keystone_ip
            auth_url = stack.keystone_auth_url
            auth_tenant = 'admin'
            auth_user = 'admin'

            # do the keystone init
            keystone_setup.initialize(auth_ip, admin_token, admin_email, admin_password, region='regionOne', ssl=None, public=None, user='heat-admin')

            # do the setup endpoints
            keystone_setup.setup_endpoints(self.build_endpoints(plan), public_host=None, region=None, os_username=auth_user, os_password=admin_password, os_tenant_name=auth_tenant, os_auth_url=auth_url)

            # do the neutron init
        except Exception:
            horizon.exceptions.handle(request,
                                      _("Unable to initialize Overcloud."))
            return False
        else:
            msg = _('Overcloud has been initialized.')
            horizon.messages.success(request, msg)
            return True

