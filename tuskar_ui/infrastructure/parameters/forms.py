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

from tuskar_ui import api


LOG = logging.getLogger(__name__)


VIRT_TYPE_CHOICES = [
    ('kvm', _("Virtualized")),
    ('qemu', _("Baremetal")),
]


class EditServiceConfig(horizon.forms.SelfHandlingForm):
    virt_type = django.forms.ChoiceField(
        label=_("Deployment Type"),
        choices=VIRT_TYPE_CHOICES,
        required=True,
        widget=django.forms.Select(attrs={
            'class': 'form-control switchable',
            'data-slug': 'virt-type',
        }),
    )

    def _get_password(self, params):
        passwords = filter(lambda param: 'SnmpdReadonlyUserPassword' in
                           param.get('name'), params)
        if len(passwords) == 0:
            password = ''
        else:
            password = passwords[0].get('value')
        return password

    def __init__(self, *args, **kwargs):
        super(EditServiceConfig, self).__init__(*args, **kwargs)
        self.plan = api.tuskar.Plan.get_the_plan(self.request)
        params = self.plan.parameter_list(
            include_key_parameters=False)
        current_password = self._get_password(params)
        self.fields['snmp_password'] = django.forms.CharField(
            label=_("SNMP Password"),
            required=False,
            initial=current_password,
            widget=django.forms.PasswordInput(attrs={
                'class': 'form-control switched',
            }))

    def _load_virt_type_parameters(self, data):
        virt_type = data.get('virt_type')
        parameters = {'compute-1::NovaComputeLibvirtType': virt_type}
        return parameters

    def _load_snmp_parameters(self, params, data):
        password = data.get('snmp_password')
        # Set the same SNMPd password in all roles.
        for role in self.plan.role_list:
            key = role.parameter_prefix + 'SnmpdReadonlyUserPassword'
            params[key] = password

    def handle(self, request, data):
        base_parameters = self._load_virt_type_parameters(data)
        self._load_snmp_parameters(base_parameters, data)
        try:
            self.plan.patch(request, self.plan.uuid, base_parameters)
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
