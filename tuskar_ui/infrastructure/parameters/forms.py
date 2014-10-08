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
    ('kvm', _("Virtualized (kvm)")),
    ('qemu', _("Baremetal (qemu)")),
]


class EditServiceConfig(horizon.forms.SelfHandlingForm):
    virt_type = django.forms.ChoiceField(
        label=_("Deployment Type"),
        choices=VIRT_TYPE_CHOICES,
        required=True,
    )
    snmp_password = django.forms.CharField(
        label=_("SNMP Password"),
        required=False,
        widget=django.forms.PasswordInput(render_value=True))

    @staticmethod
    def _load_snmp_parameters(plan, data):
        params = {}
        password = data.get('snmp_password')
        # Set the same SNMPd password in all roles.
        for role in plan.role_list:
            key = role.parameter_prefix + 'SnmpdReadonlyUserPassword'
            params[key] = password

        return params

    def handle(self, request, data):
        plan = api.tuskar.Plan.get_the_plan(self.request)
        compute_prefix = plan.get_role_by_name('compute').parameter_prefix
        virt_type = data.get('virt_type')
        parameters = {
            compute_prefix + 'NovaComputeLibvirtType': virt_type,
        }
        parameters.update(self._load_snmp_parameters(plan, data))

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
