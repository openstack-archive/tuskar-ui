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


def fieldset(self, *args, **kwargs):
    prefix=kwargs.pop('prefix', None)
    names = args or self.fields.keys()
    for name in names:
        if prefix is None or name.startswith(prefix):
            yield django.forms.forms.BoundField(
                self, self.fields[name], name)


class Action(horizon.workflows.Action):
    controller = django.forms.IntegerField(
        _("Controller"), initial=1, min_value=1,
        widget=tuskar_ui.forms.NumberInput(attrs={'class': 'input-mini', }))
    compute = django.forms.IntegerField(
        _("Compute"), initial=0, min_value=0,
        widget=tuskar_ui.forms.NumberInput(attrs={'class': 'input-mini', }))
    object_storage = django.forms.IntegerField(
        _("Object Storage"), initial=0, min_value=0,
        widget=tuskar_ui.forms.NumberInput(attrs={'class': 'input-mini', }))
    block_storage = django.forms.IntegerField(
        _("Block Storage"), initial=0, min_value=0,
        widget=tuskar_ui.forms.NumberInput(attrs={'class': 'input-mini', }))

    mysql_host_ip = django.forms.IPAddressField(
        _("Hotst IP"), required=False, widget=django.forms.TextInput(attrs={
            'placeholder': _("auto-retrieve"),
        }))
    mysql_user = django.forms.CharField(_("User"))
    mysql_password = django.forms.CharField(
        _("Password"), widget=django.forms.PasswordInput)

    amqp_host_ip = django.forms.IPAddressField(
        _("Hotst IP"), required=False, widget=django.forms.TextInput(attrs={
            'placeholder': _("auto-retrieve"),
        }))
    amqp_password = django.forms.CharField(
        _("Password"), widget=django.forms.PasswordInput)

    keystone_host_ip = django.forms.IPAddressField(
        _("Hotst IP"), required=False, widget=django.forms.TextInput(attrs={
            'placeholder': _("auto-retrieve"),
        }))
    keystone_db_password = django.forms.CharField(
        _("DB Password"), widget=django.forms.PasswordInput)
    keystone_admin_token = django.forms.CharField(
        _("Admin Token"), widget=django.forms.PasswordInput)
    keystone_admin_password = django.forms.CharField(
        _("Admin Password"), widget=django.forms.PasswordInput)

    def roles_fieldset(self):
        return fieldset(
            self, 'controller', 'compute', 'object_storage', 'block_storage')

    def mysql_fieldset(self):
        return fieldset(self, prefix="mysql_")

    def amqp_fieldset(self):
        return fieldset(self, prefix="amqp_")

    def keystone_fieldset(self):
        return fieldset(self, prefix="keystone_")

    class Meta:
        slug = 'undeployed_overview'
        name = _("Overview")


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ()
    template_name = 'infrastructure/overcloud/undeployed_overview.html'
    help_text = _("Nothing deployed yet. Design your first deployment.")
