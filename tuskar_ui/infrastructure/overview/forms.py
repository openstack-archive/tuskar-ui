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

import logging

import django.forms
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.forms
import horizon.messages
from neutronclient.common import exceptions as neutron_exceptions
from os_cloud_config import keystone as keystone_config
from os_cloud_config import neutron as neutron_config
from os_cloud_config.utils import clients

from tuskar_ui import api
import tuskar_ui.api.heat
import tuskar_ui.api.tuskar
import tuskar_ui.forms


LOG = logging.getLogger(__name__)


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
            LOG.exception()
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
            LOG.exception()
            horizon.exceptions.handle(request,
                                      _("Unable to undeploy overcloud."))
            return False
        else:
            msg = _('Undeployment in progress.')
            horizon.messages.success(request, msg)
            return True


class PostDeployInit(horizon.forms.SelfHandlingForm):
    def build_endpoints(self, plan):
        # TODO(lsmola) switch to Tuskar parameters once we are actually
        # deploying through Tuskar
        # return {
        #     "ceilometer": {
        #         "password": plan.parameter_value('CeilometerPassword')},
        #     "cinder": {
        #         "password": plan.parameter_value('CinderPassword')},
        #     "ec2": {
        #         "password": plan.parameter_value('GlancePassword')},
        #     "glance": {
        #         "password": plan.parameter_value('GlancePassword')},
        #     "heat": {
        #         "password": plan.parameter_value('HeatPassword')},
        #     "neutron": {
        #         "password": plan.parameter_value('NeutronPassword')},
        #     "nova": {
        #         "password": plan.parameter_value('NovaPassword')},
        #     "novav3": {
        #         "password": plan.parameter_value('NovaPassword')},
        #     "swift": {
        #         "password": plan.parameter_value('SwiftPassword')},
        #     "horizon": {}}

        return {
            "ceilometer": {
                "password": plan.parameter_value('CeilometerPassword')},
            "cinder": {
                "password": plan.parameter_value('CinderPassword')},
            "ec2": {
                "password": plan.parameter_value('GlancePassword')},
            "glance": {
                "password": '16b4aaa3e056d07f796a93afb6010487b7b617e7'},
            "heat": {
                "password": plan.parameter_value('HeatPassword')},
            "neutron": {
                "password": 'db051bd3a407eb8deda3c8107ed321c98ddd2450'},
            "nova": {
                "password": '67d8090ff40c0c400b08ff558233091402afc9c5'},
            "novav3": {
                "password": plan.parameter_value('NovaPassword')},
            "swift": {
                "password": plan.parameter_value('SwiftPassword')},
            "horizon": {}}

    def build_neutron_setup(self):
        # TODO(lsmola) this is default devtest params, this should probably
        # go from Tuskar parameters in the future.
        return {
            "float": {
                "name": "default-net",
                "cidr": "10.0.0.0/8"
            },
            "external": {
                "name": "ext-net",
                "allocation_start": "192.0.2.45",
                "allocation_end": "192.0.2.64",
                "cidr": "192.0.2.0/24"
            }}

    def handle(self, request, data):
        try:
            plan = api.tuskar.OvercloudPlan.get_the_plan(request)
            stack = api.heat.Stack.get_by_plan(self.request, plan)

            # TODO(lsmola) switch to Tuskar parameters once we are actually
            # deploying through Tuskar
            #admin_token = plan.parameter_value('AdminToken')
            #admin_password = plan.parameter_value('AdminPassword')
            admin_token = 'aa61677c0a270880e99293c148cefee4000b2259'
            admin_password = '5ba3a69c95c668daf84c2f103ebec82d273a4897'
            admin_email = 'example@example.org'
            auth_ip = stack.keystone_ip
            auth_url = stack.keystone_auth_url
            auth_tenant = 'admin'
            auth_user = 'admin'

            # do the keystone init
            keystone_config.initialize(
                auth_ip, admin_token, admin_email, admin_password,
                region='regionOne', ssl=None, public=None, user='heat-admin')

            # retrieve needed Overcloud clients
            keystone_client = clients.get_keystone_client(
                auth_user, admin_password, auth_tenant, auth_url)
            neutron_client = clients.get_neutron_client(
                auth_user, admin_password, auth_tenant, auth_url)

            # do the setup endpoints
            keystone_config.setup_endpoints(
                self.build_endpoints(plan), public_host=None, region=None,
                os_auth_url=auth_url, client=keystone_client)

            # do the neutron init
            try:
                neutron_config.initialize_neutron(
                    self.build_neutron_setup(),
                    neutron_client=neutron_client,
                    keystone_client=keystone_client)
            except neutron_exceptions.BadRequest as e:
                LOG.info('Neutron has been already initialized.')
                LOG.info(e.message)

        except Exception as e:
            LOG.exception(e)
            horizon.exceptions.handle(request,
                                      _("Unable to initialize Overcloud."))
            return False
        else:
            msg = _('Overcloud has been initialized.')
            horizon.messages.success(request, msg)
            return True
