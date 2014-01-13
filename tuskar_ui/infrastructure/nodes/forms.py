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

from horizon import exceptions
from tuskar_ui import api
import tuskar_ui.forms


class NodeForm(django.forms.Form):
    id = django.forms.IntegerField(
        label="",
        required=False,
        widget=django.forms.HiddenInput(),
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
        required=False,
        widget=django.forms.PasswordInput(
            render_value=False, attrs={'class': 'input input-medium'}),
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
        required=False,
        widget=django.forms.PasswordInput(
            render_value=False, attrs={'class': 'input input-medium'}),
    )
    cpus = django.forms.IntegerField(
        label=_("CPUs"),
        required=True,
        min_value=1,
        initial=1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'input input-medium'}),
    )
    memory = django.forms.IntegerField(
        label=_("Memory"),
        required=True,
        min_value=1,
        initial=1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'input input-medium'}),
    )
    local_disk = django.forms.IntegerField(
        label=_("Local Disk"),
        required=True,
        min_value=1,
        initial=1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'input input-medium'}),
    )

    def get_name(self):
        try:
            name = self.fields['ip_address'].value()
        except AttributeError:
            # when the field is not bound
            name = _("Undefined node")
        return name


class BaseNodeFormset(django.forms.formsets.BaseFormSet):
    def handle(self, request, data):
        success = True
        for form in self:
            try:
                api.Node.create(
                    request,
                    form.cleaned_data['ip_address'],
                    form.cleaned_data.get('cpus'),
                    form.cleaned_data.get('memory'),
                    form.cleaned_data.get('local_disk'),
                    [form.cleaned_data['mac_address']],
                    form.cleaned_data.get('ipmi_username'),
                    form.cleaned_data.get('ipmi_password'),
                )
            except Exception:
                success = False
                exceptions.handle(request, _('Unable to register node.'))
                # TODO(rdopieralski) Somehow find out if any port creation
                # failed and remove the mac addresses that succeeded from
                # the form.
            else:
                # TODO(rdopieralski) Remove successful nodes from formset.
                pass
        return success

    def clean(self):
        for form in self:
            if not form.cleaned_data:
                raise django.forms.ValidationError(
                    _("Please provide node data for all nodes."))


NodeFormset = django.forms.formsets.formset_factory(NodeForm, extra=1,
                                                    formset=BaseNodeFormset)
