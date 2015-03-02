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
import tuskar_ui.infrastructure.flavors.utils as flavors_utils


MATCHING_DEPLOYMENT_MODE = flavors_utils.matching_deployment_mode()
LOG = logging.getLogger(__name__)
MESSAGE_ICONS = {
    'ok': 'fa-check-square-o text-success',
    'pending': 'fa-square-o text-info',
    'error': 'fa-exclamation-circle text-danger',
    'warning': 'fa-exclamation-triangle text-warning',
    None: 'fa-exclamation-triangle text-warning',
}


def validate_roles(request, plan):
    """Validates the roles in plan and returns dict describing the issues"""
    for role in plan.role_list:
        if not role.is_valid_for_deployment(plan):
            message = {
                'text': _(u"Configure Roles."),
                'is_critical': True,
                'status': 'pending',
            }
            break
    else:
        message = {
            'text': _(u"Configure Roles."),
            'status': 'ok',
        }
    return message


def validate_global_parameters(request, plan):
    pending_required_global_params = api.tuskar.Parameter.pending_parameters(
            api.tuskar.Parameter.required_parameters(
                api.tuskar.Parameter.global_parameters(plan.parameter_list())))
    if pending_required_global_params:
        message = {
            'text': _(u"Global Service Configuration."),
            'is_critical': True,
            'status': 'pending',
        }
    else:
        message = {
            'text': _(u"Global Service Configuration."),
            'status': 'ok',
        }
    return message


def validate_plan(request, plan):
    """Validates the plan and returns a list of dicts describing the issues."""
    messages = []
    requested_nodes = 0
    for role in plan.role_list:
        node_count = plan.get_role_node_count(role)
        requested_nodes += node_count
    available_flavors = len(api.flavor.Flavor.list(request))
    if available_flavors == 0:
        messages.append({
            'text': _(u"Define Flavors."),
            'is_critical': True,
            'status': 'pending',
        })
    else:
        messages.append({
            'text': _(u"Define Flavors."),
            'status': 'ok',
        })
    available_nodes = len(api.node.Node.list(request, associated=False,
                                             maintenance=False))
    if available_nodes == 0:
        messages.append({
            'text': _(u"Register Nodes."),
            'is_critical': True,
            'status': 'pending',
        })
    elif requested_nodes > available_nodes:
        messages.append({
            'text': _(u"Not enough registered nodes for this plan. "
                      u"You need {0} more.").format(
                          requested_nodes - available_nodes),
            'is_critical': True,
            'status': 'error',
        })
    else:
        messages.append({
            'text': _(u"Register Nodes."),
            'status': 'ok',
        })
    messages.append(validate_roles(request, plan))
    messages.append(validate_global_parameters(request, plan))
    if not MATCHING_DEPLOYMENT_MODE:
        # All roles have to have the same flavor.
        default_flavor_name = api.flavor.Flavor.list(request)[0].name
        for role in plan.role_list:
            if role.flavor(plan).name != default_flavor_name:
                messages.append({
                    'text': _(u"Role {0} doesn't use default flavor.").format(
                        role.name,
                    ),
                    'is_critical': False,
                    'statis': 'error',
                })
    roles_assigned = True
    messages.append({
        'text': _(u"Assign roles."),
        'status': lambda: 'ok' if roles_assigned else 'pending',
    })
    try:
        controller_role = plan.get_role_by_name("controller")
    except KeyError:
        messages.append({
            'text': _(u"Controller Role Needed."),
            'is_critical': True,
            'status': 'error',
            'indent': 1,
        })
        roles_assigned = False
    else:
        if plan.get_role_node_count(controller_role) not in (1, 3):
            messages.append({
                'text': _(u"1 or 3 Controllers Needed."),
                'is_critical': True,
                'status': 'pending',
                'indent': 1,
            })
            roles_assigned = False
        else:
            messages.append({
                'text': _(u"1 or 3 Controllers Needed."),
                'status': 'ok',
                'indent': 1,
            })

    try:
        compute_role = plan.get_role_by_name("compute")
    except KeyError:
        messages.append({
            'text': _(u"Compute Role Needed."),
            'is_critical': True,
            'status': 'error',
            'indent': 1,
        })
        roles_assigned = False
    else:
        if plan.get_role_node_count(compute_role) < 1:
            messages.append({
                'text': _(u"1 Compute Needed."),
                'is_critical': True,
                'status': 'pending',
                'indent': 1,
            })
            roles_assigned = False
        else:
            messages.append({
                'text': _(u"1 Compute Needed."),
                'status': 'ok',
                'indent': 1,
            })
    for message in messages:
        status = message.get('status')
        if callable(status):
            message['status'] = status = status()
        message['classes'] = MESSAGE_ICONS.get(status, MESSAGE_ICONS[None])
    return messages


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
                widget=tuskar_ui.forms.NumberPickerInput(attrs={
                    'min': 1 if role.name in ('controller', 'compute') else 0,
                    'step': 2 if role.name == 'controller' else 1,
                }),
                initial=plan.get_role_node_count(role),
                required=False
            )
            field.role = role
            fields['%s-count' % role.id] = field
        return fields

    def handle(self, request, data):
        parameters = dict(
            (field.role.node_count_parameter_name, data[name])
            for (name, field) in self.fields.items() if name.endswith('-count')
        )
        # NOTE(gfidente): this is a bad hack meant to magically add the
        # parameter which enables Neutron L3 HA when the number of
        # Controllers is > 1
        try:
            controller_role = self.plan.get_role_by_name('controller')
        except Exception as e:
            LOG.warning('Unable to find role: %s', 'controller')
        else:
            if parameters[controller_role.node_count_parameter_name] > 1:
                l3ha_param = controller_role.parameter_prefix + 'NeutronL3HA'
                parameters[l3ha_param] = 'True'
        try:
            self.plan = self.plan.patch(request, self.plan.uuid, parameters)
        except Exception as e:
            horizon.exceptions.handle(request, _("Unable to update the plan."))
            LOG.exception(e)
            return False
        return True


class ScaleOut(EditPlan):
    def __init__(self, *args, **kwargs):
        super(ScaleOut, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name.endswith('-count'):
                field.widget.attrs['min'] = field.initial

    def handle(self, request, data):
        if not super(ScaleOut, self).handle(request, data):
            return False
        plan = self.plan
        try:
            stack = api.heat.Stack.get_by_plan(self.request, plan)
            stack.update(request, plan.name, plan.master_template,
                         plan.environment, plan.provider_resource_templates)
        except Exception as e:
            LOG.exception(e)
            if hasattr(e, 'error'):
                horizon.exceptions.handle(
                    request,
                    _(
                        "Unable to deploy overcloud. Reason: {0}"
                    ).format(e.error['error']['message']),
                )
                return False
            else:
                raise
        else:
            msg = _('Deployment in progress.')
            horizon.messages.success(request, msg)
            return True


class DeployOvercloud(horizon.forms.SelfHandlingForm):
    def handle(self, request, data):
        try:
            plan = api.tuskar.Plan.get_the_plan(request)
        except Exception as e:
            LOG.exception(e)
            horizon.exceptions.handle(request,
                                      _("Unable to deploy overcloud."))
            return False

        # Auto-generate missing passwords and certificates
        if plan.list_generated_parameters():
            generated_params = plan.make_generated_parameters()
            plan = plan.patch(request, plan.uuid, generated_params)

        # Validate plan and create stack
        for message in validate_plan(request, plan):
            if message['is_critical']:
                horizon.messages.success(request, message.text)
                return False
        try:
            stack = api.heat.Stack.get_by_plan(self.request, plan)
            if not stack:
                api.heat.Stack.create(request,
                                      plan.name,
                                      plan.master_template,
                                      plan.environment,
                                      plan.provider_resource_templates)
        except Exception as e:
            LOG.exception(e)
            horizon.exceptions.handle(
                request, _("Unable to deploy overcloud. Reason: {0}").format(
                    e.error['error']['message']))
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
        label=_("Float Allocation End"), initial="10.255.255.254")
    float_cidr = horizon.forms.CharField(
        label=_("Float CIDR"), initial="10.0.0.0/8")
    external_allocation_start = horizon.forms.CharField(
        label=_("External Allocation Start"), initial="172.17.0.45")
    external_allocation_end = horizon.forms.CharField(
        label=_("External Allocation End"), initial="172.17.0.64")
    external_cidr = horizon.forms.CharField(
        label=_("External CIDR"), initial="172.17.0.0/16")

    def build_endpoints(self, plan, controller_role):
        return {
            "ceilometer": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'CeilometerPassword')},
            "cinder": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'CinderPassword')},
            "ec2": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'GlancePassword')},
            "glance": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'GlancePassword')},
            "heat": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'HeatPassword')},
            "neutron": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'NeutronPassword')},
            "nova": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'NovaPassword')},
            "novav3": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'NovaPassword')},
            "swift": {
                "password": plan.parameter_value(
                    controller_role.parameter_prefix + 'SwiftPassword'),
                'path': '/v1/AUTH_%(tenant_id)s',
                'admin_path': '/v1'},
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
            controller_role = plan.get_role_by_name("controller")
            stack = api.heat.Stack.get_by_plan(self.request, plan)

            admin_token = plan.parameter_value(
                controller_role.parameter_prefix + 'AdminToken')
            admin_password = plan.parameter_value(
                controller_role.parameter_prefix + 'AdminPassword')
            admin_email = data['admin_email']
            auth_ip = stack.keystone_ip
            auth_url = stack.keystone_auth_url
            auth_tenant = 'admin'
            auth_user = 'admin'

            # do the keystone init
            keystone_config.initialize(
                auth_ip, admin_token, admin_email, admin_password,
                region='regionOne', ssl=None, public=None, user='heat-admin',
                pki_setup=False)

            # retrieve needed Overcloud clients
            keystone_client = clients.get_keystone_client(
                auth_user, admin_password, auth_tenant, auth_url)
            neutron_client = clients.get_neutron_client(
                auth_user, admin_password, auth_tenant, auth_url)

            # do the setup endpoints
            keystone_config.setup_endpoints(
                self.build_endpoints(plan, controller_role),
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
