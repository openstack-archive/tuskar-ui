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
import logging

import django.forms
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.forms
import horizon.messages

from tuskar_ui import api
import tuskar_ui.forms
from tuskar_ui.utils import utils


LOG = logging.getLogger(__name__)


VIRT_TYPE_CHOICES = [
    ('qemu', _("Virtualized (qemu)")),
    ('kvm', _("Baremetal (kvm)")),
]

CINDER_ISCSI_HELPER_CHOICES = [
    ('tgtadm', _('tgtadm')),
    ('lioadm', _('lioadm')),
]


class ParameterAwareMixin(object):
    parameter = None


def parameter_fields(request, prefix=None, read_only=False):
    fields = SortedDict()
    plan = api.tuskar.Plan.get_the_plan(request)
    parameters = plan.parameter_list(include_key_parameters=False)

    for p in parameters:
        if prefix and not p.name.startswith(prefix):
            continue
        Field = django.forms.CharField
        field_kwargs = {}
        widget = None
        if read_only:
            if p.hidden:
                widget = tuskar_ui.forms.StaticTextPasswordWidget
            else:
                widget = tuskar_ui.forms.StaticTextWidget
        else:
            if p.hidden:
                widget = django.forms.PasswordInput(render_value=True)
            elif p.parameter_type == 'number':
                Field = django.forms.IntegerField
            elif p.parameter_type == 'boolean':
                Field = django.forms.BooleanField
            elif (p.parameter_type == 'string' and
                    p.get_constraint_by_type('allowed_values')):
                Field = django.forms.ChoiceField
                field_kwargs['choices'] = [
                    (choice, choice) for choice in
                    p.get_constraint_by_type('allowed_values')['definition']]
            elif (p.parameter_type in ['json', 'comma_delimited_list'] or
                  'Certificate' in p.name):
                widget = django.forms.Textarea

        fields[p.name] = Field(
            required=False,
            label=_parameter_label(p),
            initial=p.value,
            widget=widget,
            **field_kwargs
        )
        fields[p.name].__class__ = type('ParameterAwareField',
                                        (ParameterAwareMixin, Field), {})
        fields[p.name].parameter = p
    return fields


def _parameter_label(parameter):
    return tuskar_ui.forms.label_with_tooltip(
        parameter.label or utils.de_camel_case(parameter.stripped_name),
        parameter.description)


class ServiceConfig(horizon.forms.SelfHandlingForm):
    def __init__(self, *args, **kwargs):
        super(ServiceConfig, self).__init__(*args, **kwargs)
        self.fields.update(parameter_fields(self.request, read_only=True))

    def global_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='^(?!.*::)')

    def controller_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='Controller-1')

    def compute_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='Compute-1')

    def block_storage_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='Cinder-Storage-1')

    def object_storage_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='Swift-Storage-1')

    def ceph_storage_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='Ceph-Storage-1')

    def handle():
        pass


class AdvancedEditServiceConfig(ServiceConfig):
    def __init__(self, *args, **kwargs):
        super(AdvancedEditServiceConfig, self).__init__(*args, **kwargs)
        self.fields.update(parameter_fields(self.request))

    def handle(self, request, data):
        plan = api.tuskar.Plan.get_the_plan(self.request)

        # TODO(bcrochet): Commenting this out.
        # For advanced config, we should have a whitelist of which params
        # must be synced across roles.
        # data = self._sync_common_params_across_roles(plan, data)

        try:
            plan.patch(request, plan.uuid, data)
        except Exception as e:
            horizon.exceptions.handle(
                request,
                _("Unable to update the service configuration."))
            LOG.exception(e)
            return False
        else:
            horizon.messages.success(
                request,
                _("Service configuration updated."))
            return True

    @staticmethod
    def _sync_common_params_across_roles(plan, parameters_dict):
        for (p_key, p_value) in parameters_dict.iteritems():
            for role in plan.role_list:
                role_parameter_key = (role.parameter_prefix +
                                      api.tuskar.strip_prefix(p_key))
                if role_parameter_key in parameters_dict:
                    parameters_dict[role_parameter_key] = p_value
        return parameters_dict


class SimpleEditServiceConfig(horizon.forms.SelfHandlingForm):
    virt_type = django.forms.ChoiceField(
        label=_("Deployment Type"),
        choices=VIRT_TYPE_CHOICES,
        required=True,
        help_text=_('If you are testing OpenStack in a virtual machine, '
                    'you must configure Compute to use qemu without KVM '
                    'and hardware virtualization.'))
    neutron_public_interface = django.forms.CharField(
        label=_("Public Interface"),
        required=True,
        initial='eth0',
        help_text=_('What interface to bridge onto br-ex for network nodes. '
                    'If you are testing OpenStack in a virtual machine'
                    'you must configure interface to eth0.'))
    snmp_password = django.forms.CharField(
        label=_("SNMP Password"),
        required=True,
        help_text=_('The user password for SNMPd with readonly '
                    'rights running on all Overcloud nodes'),
        widget=django.forms.PasswordInput(render_value=True))
    cloud_name = django.forms.CharField(
        label=_("Cloud name"),
        required=True,
        initial="overcloud",
        help_text=_('The DNS name of this cloud. '
                    'E.g. ci-overcloud.tripleo.org'))
    cinder_iscsi_helper = django.forms.ChoiceField(
        label=_("Cinder ISCSI helper"),
        choices=CINDER_ISCSI_HELPER_CHOICES,
        required=True,
        help_text=_('The iSCSI helper to use with cinder.'))
    ntp_server = django.forms.CharField(
        label=_("NTP server"),
        required=False,
        initial="",
        help_text=_('Address of the NTP server. If blank, public NTP servers '
                    'will be used.'))
    extra_config = django.forms.CharField(
        label=_("Extra Config"),
        required=False,
        widget=django.forms.Textarea(attrs={'rows': 2}),
        help_text=("Additional configuration to inject into the cluster."
                   "The data format of this field is JSON."
                   "See http://git.io/PuwLXQ for more information."))

    def clean_extra_config(self):
        data = self.cleaned_data['extra_config']
        try:
            json.loads(data)
        except Exception as json_error:
            raise django.forms.ValidationError(
                _("%(err_msg)s"), params={'err_msg': json_error.message})
        return data

    @staticmethod
    def _load_additional_parameters(plan, data, form_key, param_name):
        params = {}
        param_value = data.get(form_key)
        # Set the same parameter and value in all roles.
        for role in plan.role_list:
            key = role.parameter_prefix + param_name
            if key in [parameter.name
                       for parameter in role.parameter_list(plan)]:
                params[key] = param_value

        return params

    def handle(self, request, data):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        compute_prefix = plan.get_role_by_name('Compute').parameter_prefix
        controller_prefix = plan.get_role_by_name(
            'Controller').parameter_prefix
        cinder_prefix = plan.get_role_by_name(
            'Cinder-Storage').parameter_prefix

        virt_type = data.get('virt_type')
        neutron_public_interface = data.get('neutron_public_interface')
        cloud_name = data.get('cloud_name')
        cinder_iscsi_helper = data.get('cinder_iscsi_helper')
        ntp_server = data.get('ntp_server')

        parameters = {
            compute_prefix + 'NovaComputeLibvirtType': virt_type,
            controller_prefix + 'CinderISCSIHelper': cinder_iscsi_helper,
            cinder_prefix + 'CinderISCSIHelper': cinder_iscsi_helper,
            controller_prefix + 'CloudName': cloud_name,
            controller_prefix + 'NeutronPublicInterface':
                neutron_public_interface,
            compute_prefix + 'NeutronPublicInterface':
                neutron_public_interface,
            controller_prefix + 'NtpServer':
                ntp_server,
            compute_prefix + 'NtpServer':
                ntp_server,
        }

        parameters.update(self._load_additional_parameters(
            plan, data,
            'snmp_password', 'SnmpdReadonlyUserPassword'))
        parameters.update(self._load_additional_parameters(
            plan, data,
            'extra_config', 'ExtraConfig'))

        try:
            plan.patch(request, plan.uuid, parameters)
        except Exception as e:
            horizon.exceptions.handle(
                request,
                _("Unable to update the service configuration."))
            LOG.exception(e)
            return False
        else:
            horizon.messages.success(
                request,
                _("Service configuration updated."))
            return True
