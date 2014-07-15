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


ARCHITECTURE_CHOICES = [
    ('x86', _("x86")),
    ('x86_64', _("x86_64")),
]
DRIVER_CHOICES = [
    ('ipmi', _("IPMI Driver")),
    ('dummy', _("Dummy Driver")),
]


class NodeForm(django.forms.Form):
    id = django.forms.IntegerField(
        label="",
        required=False,
        widget=django.forms.HiddenInput(),
    )

    driver = django.forms.ChoiceField(
        label=_("Driver"),
        choices=DRIVER_CHOICES,
        required=True,
        widget=django.forms.Select(attrs={
            'class': 'input input-medium switchable',
            'data-slug': 'driver',
        }),
    )

    ipmi_address = django.forms.IPAddressField(
        label=_("IPMI Address"),
        required=False,
        widget=django.forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'driver',
            'data-driver-ipmi': 'ipmi',
        }),
    )
    ipmi_username = django.forms.CharField(
        label=_("IPMI User"),
        required=False,
        widget=django.forms.TextInput(attrs={
            'class': 'input input-medium switched',
            'data-switch-on': 'driver',
            'data-driver-ipmi': 'ipmi',
        }),
    )
    ipmi_password = django.forms.CharField(
        label=_("IPMI Password"),
        required=False,
        widget=django.forms.PasswordInput(render_value=False, attrs={
            'class': 'input input-medium switched',
            'data-switch-on': 'driver',
            'data-driver-ipmi': 'ipmi',
        }),
    )
    mac_addresses = tuskar_ui.forms.MultiMACField(
        label=_("NIC MAC Addresses"),
        widget=django.forms.Textarea(attrs={
            'class': 'input input-medium',
            'rows': '2',
        }),
    )

    architecture = django.forms.ChoiceField(
        label=_("Architecture"),
        required=True,
        choices=ARCHITECTURE_CHOICES,
        widget=django.forms.Select(
            attrs={'class': 'input input-medium'}),
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
            # FIXME(lsmola) show somethign meaningful here
            name = self.fields['ipmi_address'].value()
        except AttributeError:
            # when the field is not bound
            name = _("Undefined node")
        return name


class BaseNodeFormset(django.forms.formsets.BaseFormSet):
    def handle(self, request, data):
        success = True
        for form in self:
            data = form.cleaned_data
            try:
                api.node.Node.create(
                    request,
                    # TODO(rdopieralski) If ipmi_address is no longer required,
                    # then we will need to use something else here?
                    ipmi_address=data['ipmi_address'],
                    architecture=data.get('architecture'),
                    cpus=data.get('cpus'),
                    memory=data.get('memory'),
                    local_disk=data.get('local_disk'),
                    mac_addresses=data['mac_addresses'].split(),
                    ipmi_username=data.get('ipmi_username'),
                    ipmi_password=data.get('ipmi_password'),
                    driver=form.cleaned_data.get('driver'),
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
            if not form.cleaned_data.get('ipmi_username'):
                form.cleaned_data['ipmi_username'] = None
            if not form.cleaned_data.get('ipmi_password'):
                form.cleaned_data['ipmi_password'] = None


NodeFormset = django.forms.formsets.formset_factory(NodeForm, extra=1,
                                                    formset=BaseNodeFormset)
