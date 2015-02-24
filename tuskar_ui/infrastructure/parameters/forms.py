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
    ('kvm', _("Baremetal (kvm)")),
    ('qemu', _("Virtualized (qemu)")),
]

NEUTRON_PUBLIC_INTERFACE_CHOICES = [
    ('em2', _("Baremetal (em2)")),
    ('eth0', _("Virtualized (eth0)")),
]

CINDER_ISCSI_HELPER_CHOICES = [
    ('tgtadm', _('tgtadm')),
    ('lioadm', _('lioadm')),
]


def parameter_fields(request, prefix=None, read_only=False):
    fields = SortedDict()
    plan = api.tuskar.Plan.get_the_plan(request)
    parameters = plan.parameter_list(include_key_parameters=False)

    for p in parameters:
        if prefix and not p.name.startswith(prefix):
            continue
        kwargs = {}
        if read_only:
            if p.hidden:
                kwargs['widget'] = tuskar_ui.forms.StaticTextPasswordWidget
            else:
                kwargs['widget'] = tuskar_ui.forms.StaticTextWidget
            Field = django.forms.CharField
        else:
            if p.hidden:
                Field = django.forms.CharField
                kwargs['widget'] = (
                    django.forms.PasswordInput(render_value=True))
            elif p.type == 'number':
                Field = django.forms.IntegerField
            elif p.type == 'boolean':
                Field = django.forms.BooleanField
            elif (p.type == 'string' and
                    p.constraints['allowed_values']['definition']):
                Field = django.forms.ChoiceField
                kwargs['choices'] = (
                    p.constraints['allowed_values']['definition'])
            else:
                if (p.type in ['json', 'comma_delimited_list'] or
                        'Certificate' in p.name):
                    kwargs['widget'] = django.forms.Textarea
                Field = django.forms.CharField

        fields[p.name] = Field(required=False,
                               label=_parameter_label(p),
                               initial=p.value,
                               **kwargs)
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
        return tuskar_ui.forms.fieldset(self, prefix='controller-1')

    def compute_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='compute-1')

    def block_storage_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='cinder-storage-1')

    def object_storage_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix='swift-storage-1')

    def handle():
        pass


class AdvancedEditServiceConfig(ServiceConfig):
    def __init__(self, *args, **kwargs):
        super(AdvancedEditServiceConfig, self).__init__(*args, **kwargs)
        self.fields.update(parameter_fields(self.request))

    def handle(self, request, data):
        plan = api.tuskar.Plan.get_the_plan(self.request)

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


class SimpleEditServiceConfig(horizon.forms.SelfHandlingForm):
    virt_type = django.forms.ChoiceField(
        label=_("Deployment Type"),
        choices=VIRT_TYPE_CHOICES,
        required=True,
        help_text=_('If you are testing OpenStack in a virtual machine, '
                    'you must configure Compute to use qemu without KVM '
                    'and hardware virtualization.'))
    neutron_public_interface = django.forms.ChoiceField(
        label=_("Public Interface"),
        choices=NEUTRON_PUBLIC_INTERFACE_CHOICES,
        required=True,
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
            params[key] = param_value

        return params

    def handle(self, request, data):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        compute_prefix = plan.get_role_by_name('compute').parameter_prefix
        controller_prefix = plan.get_role_by_name(
            'controller').parameter_prefix
        cinder_prefix = plan.get_role_by_name(
            'cinder-storage').parameter_prefix

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
