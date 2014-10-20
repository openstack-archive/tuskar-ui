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

from django.core.urlresolvers import reverse_lazy
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


def validate_plan(request, plan):
    """Validates the plan and returns a list of dicts describing the issues."""
    messages = []
    try:
        controller_role = plan.get_role_by_name("controller")
    except KeyError:
        messages.append({
            'text': _(u"No controller role."),
            'is_critical': True,
        })
    else:
        if plan.get_role_node_count(controller_role) not in (1, 3):
            messages.append({
                'text': _(u"You should have either 1 or 3 controller nodes."),
                'is_critical': True,
            })
    try:
        compute_role = plan.get_role_by_name("compute")
    except KeyError:
        messages.append({
            'text': _(u"No compute role."),
            'is_critical': True,
        })
    else:
        if plan.get_role_node_count(compute_role) < 1:
            messages.append({
                'text': _(u"You need at least 1 compute node."),
                'is_critical': True,
            })
    requested_nodes = 0
    previous_snmp_password = None
    for role in plan.role_list:
        if role.image(plan) is None:
            messages.append({
                'text': _(u"Role {0} has no image.").format(role.name),
                'is_critical': True,
                'link_url': reverse_lazy('horizon:infrastructure:roles:index'),
                'link_label': _(u"Associate this role with an image."),
            })
        if role.flavor(plan) is None:
            messages.append({
                'text': _(u"Role {0} has no flavor.").format(role.name),
                'is_critical': False,
                'link_url': reverse_lazy('horizon:infrastructure:roles:index'),
                'link_label': _(u"Associate this role with a flavor."),
            })
        requested_nodes += plan.get_role_node_count(role)
        snmp_password = plan.parameter_value(
            role.parameter_prefix + 'SnmpdReadonlyUserPassword')
        if (not snmp_password or
                previous_snmp_password and
                previous_snmp_password != snmp_password):
            messages.append({
                'text': _(
                    u"Set your SNMP password for role {0}.").format(role.name),
                'is_critical': True,
                'link_url': reverse_lazy(
                    'horizon:infrastructure:parameters:index'),
                'link_label': _(u"Configure."),
            })
        previous_snmp_password = snmp_password
    available_flavors = len(api.flavor.Flavor.list(request))
    if available_flavors == 0:
        messages.append({
            'text': _(u"You have no flavors defined."),
            'is_critical': True,
            'link_url': reverse_lazy('horizon:infrastructure:flavors:index'),
            'link_label': _(u"Define flavors."),
        })
    available_nodes = len(api.node.Node.list(request, associated=False,
                                             maintenance=False))
    if available_nodes == 0:
            messages.append({
                'text': _(u"You have no nodes available."),
                'is_critical': True,
                'link_url': reverse_lazy('horizon:infrastructure:nodes:index'),
                'link_label': _(u"Register nodes."),
            })
    elif requested_nodes > available_nodes:
            messages.append({
                'text': _(u"Not enough registered nodes for this plan. "
                          u"You need {0} more.").format(
                              requested_nodes - available_nodes),
                'is_critical': True,
                'link_url': reverse_lazy('horizon:infrastructure:nodes:index'),
                'link_label': _(u"Register more nodes."),
            })
    # TODO(rdopieralski) Add more checks.
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
        try:
            self.plan = self.plan.patch(request, self.plan.uuid, parameters)
        except Exception as e:
            horizon.exceptions.handle(request, _("Unable to update the plan."))
            LOG.exception(e)
            return False
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
