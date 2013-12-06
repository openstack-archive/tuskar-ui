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
from django.utils.translation import ugettext_lazy as _  # noqa
import horizon.forms

import tuskar_ui.forms


class NodeForm(django.forms.Form):
    id = django.forms.IntegerField(
        label="",
        required=False,
        widget=django.forms.HiddenInput(),
    )
    node_tags = django.forms.CharField(
        label=_("Node Tags"),
        required=False,
        widget=django.forms.Textarea(attrs={
            'class': 'input input-medium',
            'rows': 2,
        }),
    )

    ip_address = django.forms.IPAddressField(
        label=_("IP Address"),
        widget=django.forms.TextInput(attrs={'class': 'input input-medium'}),
    )
    ipmi_user = django.forms.CharField(
        label=_("IPMI User"),
        required=False,
        widget=django.forms.TextInput(attrs={'class': 'input input-medium'}),
    )
    ipmi_password = django.forms.CharField(
        label=_("IPMI Password"),
        widget=django.forms.PasswordInput(render_value=False,
            attrs={'class': 'input input-medium'}),
    )

    mac_address = tuskar_ui.forms.MACField(
        label=_("NIC MAC Address"),
        widget=django.forms.Textarea(attrs={
            'class': 'input input-medium',
            'rows': 2,
        }),
    )

    ipmi_user = django.forms.CharField(
        label=_("IPMI User"),
        required=False,
        widget=django.forms.TextInput(attrs={'class': 'input input-medium'}),
    )
    ipmi_password = django.forms.CharField(
        label=_("IPMI Password"),
        widget=django.forms.PasswordInput(render_value=False,
            attrs={'class': 'input input-medium'}),
    )
    introspect_hardware = django.forms.BooleanField(
        label=_("Auto-discover values"),
        required=False,
        initial=True,
    )
    cpus = django.forms.IntegerField(
        label=_("CPUs"),
        required=False,
        min_value = 1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'input input-medium', 'disabled': True}),
    )
    memory = django.forms.IntegerField(
        label=_("Memory"),
        required=False,
        min_value = 1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'input input-medium', 'disabled': True}),
    )
    local_disk = django.forms.IntegerField(
        label=_("Local Disk"),
        required=False,
        min_value = 1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'input input-medium', 'disabled': True}),
    )


class BaseNodeFormset(django.forms.formsets.BaseFormSet):
    def handle(self, request, data):
        for form in self:
            # TODO(rdopieralski) Create the nodes here.
            print form.cleaned_data
        return True


NodeFormset = django.forms.formsets.formset_factory(
    NodeForm, extra=1, can_delete=True, formset=BaseNodeFormset)
