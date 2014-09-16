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
from os_cloud_config import keystone as keystone_setup

from tuskar_ui import api
import tuskar_ui.api.heat
import tuskar_ui.api.tuskar
import tuskar_ui.forms


LOG = logging.getLogger(__name__)
_ROLES_BY_NAME = None


def _get_role_by_name(plan, role_name):
    global _ROLES_BY_NAME
    if _ROLES_BY_NAME is None:
        _ROLES_BY_NAME = {}
        for role in plan.role_list:
            _ROLES_BY_NAME[role.name] = role
    return _ROLES_BY_NAME[role_name]


def _get_role_count(plan, role):
    return plan.parameter_value(role.node_count_parameter_name, 0)


def validate_plan(request, plan):
    """Validates the plan and returns a list of dicts describing the issues."""
    messages = []
    try:
        controller_role = _get_role_by_name(plan, "Controller")
    except KeyError:
        messages.append({
            'text': _(u"No controller role."),
            'is_critical': True,
            'link_url': reverse_lazy('horizon:infrastructure:roles:index'),
            'link_label': _(u"Create role."),
        })
    else:
        if _get_role_count(plan, controller_role) not in (1, 3):
            messages.append({
                'text': _(u"You should have either 1 or 3 controller nodes."),
                'is_critical': True,
            })
    try:
        compute_role = _get_role_by_name(plan, "Compute")
    except KeyError:
        messages.append({
            'text': _(u"No compute role."),
            'is_critical': True,
            'link_url': reverse_lazy('horizon:infrastructure:roles:index'),
            'link_label': _(u"Create role."),
        })
    else:
        if _get_role_count(plan, compute_role) < 1:
            messages.append({
                'text': _(u"You need at least 1 compute node."),
                'is_critical': True,
            })
    requested_nodes = 0
    for role in plan.role_list:
        if role.image(plan) is None:
            messages.append({
                'text': _(u"Role %s has no image.") % role.name,
                'is_critical': False,
                'link_url': reverse_lazy('horizon:infrastructure:roles:index'),
                'link_label': _(u"Associate this role with an image."),
            })
        if role.flavor(plan) is None:
            messages.append({
                'text': _(u"Role %s has no flavor.") % role.name,
                'is_critical': False,
                'link_url': reverse_lazy('horizon:infrastructure:roles:index'),
                'link_label': _(u"Associate this role with a flavor."),
            })
        requested_nodes += int(_get_role_count(plan, role) or 0)
    available_flavors = len(api.flavor.Flavor.list(request))
    if available_flavors == 0:
        messages.append({
            'text': _(u"You have no flavors defined."),
            'is_critical': True,
            'link_url': reverse_lazy('horizon:infrastructure:flavors:index'),
            'link_label': _(u"Define flavors."),
        })
    availalble_nodes = len(api.node.Node.list(request, associated=False))
    if availalble_nodes == 0:
            messages.append({
                'text': _(u"You have no nodes available."),
                'is_critical': True,
                'link_url': reverse_lazy('horizon:infrastructure:nodes:index'),
                'link_label': _(u"Register nodes."),
            })
    elif requested_nodes > availalble_nodes:
            messages.append({
                'text': _(u"Not enough registered nodes for this plan. "
                          u"You need %d more.") % (
                              requested_nodes - availalble_nodes),
                'is_critical': True,
                'link_url': reverse_lazy('horizon:infrastructure:nodes:index'),
                'link_label': _(u"Register more nodes."),
            })
    compute_snmp_password = plan.parameter_value(
        'compute-1::SnmpdReadonlyUserPassword')
    controller_snmp_password = plan.parameter_value(
        'controller-1::SnmpdReadonlyUserPassword')
    if (not compute_snmp_password or
            compute_snmp_password != controller_snmp_password):
        messages.append({
            'text': _(u"Set your SNMP password."),
            'is_critical': True,
            'link_url': reverse_lazy(
                'horizon:infrastructure:parameters:index'),
            'link_label': _(u"Configure."),
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
                widget=tuskar_ui.forms.NumberPickerInput,
                initial=_get_role_count(plan, role),
                # XXX Dirty hack for requiring a controller node.
                required=(role.name in ('Controller', 'Compute')),
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
        except Exception as e:
            LOG.exception(e)
            horizon.exceptions.handle(request,
                                      _("Unable to deploy overcloud."))
            return False
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
    def build_endpoints(self, plan):
        return {
            "ceilometer": {
                "password": plan.parameter_value('CeilometerPassword')},
            "cinder": {
                "password": plan.parameter_value('CinderPassword')},
            "ec2": {
                "password": plan.parameter_value('GlancePassword')},
            "glance": {
                "password": plan.parameter_value('GlancePassword')},
            "heat": {
                "password": plan.parameter_value('HeatPassword')},
            "neutron": {
                "password": plan.parameter_value('NeutronPassword')},
            "nova": {
                "password": plan.parameter_value('NovaPassword')},
            "novav3": {
                "password": plan.parameter_value('NovaPassword')},
            "swift": {
                "password": plan.parameter_value('SwiftPassword')},
            "horizon": {'port': ''}}

    def handle(self, request, data):
        try:
            plan = api.tuskar.Plan.get_the_plan(request)
            stack = api.heat.Stack.get_by_plan(self.request, plan)

            admin_token = plan.parameter_value('AdminToken')
            admin_password = plan.parameter_value('AdminPassword')
            admin_email = 'example@example.org'
            auth_ip = stack.keystone_ip
            auth_url = stack.keystone_auth_url
            auth_tenant = 'admin'
            auth_user = 'admin'

            # do the keystone init
            keystone_setup.initialize(
                auth_ip, admin_token, admin_email, admin_password,
                region='regionOne', ssl=None, public=None, user='heat-admin')

            # do the setup endpoints
            keystone_setup.setup_endpoints(
                self.build_endpoints(plan), public_host=None, region=None,
                os_username=auth_user, os_password=admin_password,
                os_tenant_name=auth_tenant, os_auth_url=auth_url)

            # do the neutron init
            # TODO(lsmola) neutron needs to be prepared in os-cloud-config

        except Exception as e:
            LOG.exception(e)
            horizon.exceptions.handle(request,
                                      _("Unable to initialize Overcloud."))
            return False
        else:
            msg = _('Overcloud has been initialized.')
            horizon.messages.success(request, msg)
            return True
