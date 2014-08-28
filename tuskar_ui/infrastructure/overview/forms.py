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
            field.role = role
            fields['%s-count' % role.id] = field
        return fields

    def handle(self, request, data):
        parameters = dict(
            (field.role.node_count_parameter_name, data[name])
            for (name, field) in self.fields.items() if name.endswith('-count')
        )
        try:
            self.plan.patch(request, self.plan.uuid, parameters)
        except Exception as e:
            horizon.exceptions.handle(request, _("Unable to update the plan."))
            LOG.exception(e)
            return False
        else:
            horizon.messages.success(request, _("Plan updated."))
            return True


class DeployOvercloud(horizon.forms.SelfHandlingForm):
    def handle(self, request, data):
        try:
            plan = api.tuskar.Plan.get_the_plan(request)
            stack = api.heat.Stack.get_by_plan(self.request, plan)
            if not stack:
                api.heat.Stack.create(request,
                                      plan.name,
                                      plan.master_template,
                                      plan.environment,
                                      plan.provider_resource_templates)
        except Exception as e:
            LOG.exception(e)
            horizon.exceptions.handle(request,
                                      _("Unable to deploy overcloud."))
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
        except Exception as e:
            LOG.exception(e)
            horizon.exceptions.handle(request,
                                      _("Unable to undeploy overcloud."))
            return False
        else:
            msg = _('Undeployment in progress.')
            horizon.messages.success(request, msg)
            return True


class PostDeployInit(horizon.forms.SelfHandlingForm):
    # TODO(lsmola) put here signed user email, has to be done dynamically
    # in init
    admin_email = horizon.forms.CharField(
        label=_("Admin Email"), initial="example@example.org")
    public_host = horizon.forms.CharField(
        label=_("Public Host"), initial="", required=False)
    region = horizon.forms.CharField(
        label=_("Region"), initial="regionOne")
    float_allocation_start = horizon.forms.CharField(
        label=_("Float Allocation Start"), initial="10.0.0.2")
    float_allocation_end = horizon.forms.CharField(
        label=_("Float Allocation Start"), initial="10.255.255.254")
    float_cidr = horizon.forms.CharField(
        label=_("Float CIDR"), initial="10.0.0.0/8")
    external_allocation_start = horizon.forms.CharField(
        label=_("External Allocation Start"), initial="192.0.2.45")
    external_allocation_end = horizon.forms.CharField(
        label=_("External Allocation Start"), initial="192.0.2.64")
    external_cidr = horizon.forms.CharField(
        label=_("External CIDR"), initial="192.0.2.0/24")

    def build_endpoints(self, plan):
        return {
            "ceilometer": {
                "password": plan.parameter_value(
                    'controller-1::CeilometerPassword')},
            "cinder": {
                "password": plan.parameter_value(
                    'controller-1::CinderPassword')},
            "ec2": {
                "password": plan.parameter_value(
                    'controller-1::GlancePassword')},
            "glance": {
                "password": plan.parameter_value(
                    'controller-1::GlancePassword')},
            "heat": {
                "password": plan.parameter_value(
                    'controller-1::HeatPassword')},
            "neutron": {
                "password": plan.parameter_value(
                    'controller-1::NeutronPassword')},
            "nova": {
                "password": plan.parameter_value(
                    'controller-1::NovaPassword')},
            "novav3": {
                "password": plan.parameter_value(
                    'controller-1::NovaPassword')},
            "swift": {
                "password": plan.parameter_value(
                    'controller-1::SwiftPassword')},
            "horizon": {'port': ''}}

    def build_neutron_setup(self, data):
        # TODO(lsmola) this is default devtest params, this should probably
        # go from Tuskar parameters in the future.
        return {
            "float": {
                "name": "default-net",
                "allocation_start": data['float_allocation_start'],
                "allocation_end": data['float_allocation_end'],
                "cidr": data['float_cidr']
            },
            "external": {
                "name": "ext-net",
                "allocation_start": data['external_allocation_start'],
                "allocation_end": data['external_allocation_end'],
                "cidr": data['external_cidr']
            }}

    def handle(self, request, data):
        try:
            plan = api.tuskar.Plan.get_the_plan(request)
            stack = api.heat.Stack.get_by_plan(self.request, plan)

            admin_token = plan.parameter_value('controller-1::AdminToken')
            admin_password = plan.parameter_value(
                'controller-1::AdminPassword')
            admin_email = data['admin_email']
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
                self.build_endpoints(plan),
                public_host=data['public_host'],
                region=data['region'],
                os_auth_url=auth_url,
                client=keystone_client)

            # do the neutron init
            try:
                neutron_config.initialize_neutron(
                    self.build_neutron_setup(data),
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
