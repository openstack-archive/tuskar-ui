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
import horizon.workflows

import tuskar_ui.forms


class Action(horizon.workflows.Action):
    mysql_host_ip = django.forms.IPAddressField(
        label=_("Hotst IP"), required=False,
        widget=django.forms.TextInput(attrs={
            'placeholder': _("auto-retrieve"),
        }))
    mysql_user = django.forms.CharField(_("User"))
    mysql_password = django.forms.CharField(
        label=_("Password"), widget=django.forms.PasswordInput)

    amqp_host_ip = django.forms.IPAddressField(
        label=_("Hotst IP"), required=False,
        widget=django.forms.TextInput(attrs={
            'placeholder': _("auto-retrieve"),
        }))
    amqp_password = django.forms.CharField(
        label=_("Password"), widget=django.forms.PasswordInput)

    keystone_host_ip = django.forms.IPAddressField(
        label=_("Hotst IP"), required=False,
        widget=django.forms.TextInput(attrs={
            'placeholder': _("auto-retrieve"),
        }))
    keystone_db_password = django.forms.CharField(
        label=_("DB Password"), widget=django.forms.PasswordInput)
    keystone_admin_token = django.forms.CharField(
        label=_("Admin Token"), widget=django.forms.PasswordInput)
    keystone_admin_password = django.forms.CharField(
        label=_("Admin Password"), widget=django.forms.PasswordInput)

    class Meta:
        slug = 'deployed_configuration'
        name = _("Configuration")

    def mysql_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix="mysql_")

    def amqp_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix="amqp_")

    def keystone_fieldset(self):
        return tuskar_ui.forms.fieldset(self, prefix="keystone_")

    def handle(self, request, context):
        context['configuration'] = self.cleaned_data
        return context


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ('configuration',)
    template_name = 'infrastructure/overcloud/undeployed_configuration.html'


