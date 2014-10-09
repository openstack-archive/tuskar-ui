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

import csv

import django.forms
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms

from tuskar_ui import api
import tuskar_ui.forms


CPU_ARCH_CHOICES = [
    ('amd64', _("amd64")),
    ('x86', _("x86")),
    ('x86_64', _("x86_64")),
]
DRIVER_CHOICES = [
    ('ipmi', _("IPMI Driver")),
    ('pxe_ssh', _("PXE + SSH")),
]


def get_driver_info_dict(data):
    driver = data['driver']
    driver_dict = {
        'driver': driver
    }
    if driver == 'ipmi':
        driver_dict.update(
            # TODO(rdopieralski) If ipmi_address is no longer required,
            # then we will need to use something else here?
            ipmi_address=data['ipmi_address'],
            ipmi_username=data.get('ipmi_username'),
            ipmi_password=data.get('ipmi_password'),
        )
    elif driver == 'pxe_ssh':
        driver_dict.update(
            ssh_address=data['ssh_address'],
            ssh_username=data['ssh_username'],
            ssh_key_contents=data['ssh_key_contents'],
        )
    return driver_dict


def auto_discover_node(request, kwargs):
    node = api.node.Node.create(
        request,
        **kwargs
    )
    api.node.Node.set_maintenance(request,
                                  node.uuid,
                                  True)
    api.node.Node.discover(request, [node.uuid])


class BaseNodeForm(django.forms.Form):
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
            'class': 'form-control switchable',
            'data-slug': 'driver',
        }),
    )

    ipmi_address = django.forms.IPAddressField(
        label=_("IPMI Address"),
        required=False,
        widget=django.forms.TextInput(attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-ipmi': _("IPMI Driver"),
        }),
    )
    ipmi_username = django.forms.CharField(
        label=_("IPMI User"),
        required=False,
        widget=django.forms.TextInput(attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-ipmi': _("IPMI Driver"),
        }),
    )
    ipmi_password = django.forms.CharField(
        label=_("IPMI Password"),
        required=False,
        widget=django.forms.PasswordInput(render_value=False, attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-ipmi': _("IPMI Driver"),
        }),
    )
    ssh_address = django.forms.IPAddressField(
        label=_("SSH Address"),
        required=False,
        widget=django.forms.TextInput(attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-pxe_ssh': _("PXE + SSH"),
        }),
    )
    ssh_username = django.forms.CharField(
        label=_("SSH User"),
        required=False,
        widget=django.forms.TextInput(attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-pxe_ssh': _("PXE + SSH"),
        }),
    )
    ssh_key_contents = django.forms.CharField(
        label=_("SSH Key Contents"),
        required=False,
        widget=django.forms.Textarea(attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-pxe_ssh': _("PXE + SSH"),
            'rows': 2,
        }),
    )

    def get_name(self):
        try:
            name = (self.fields['ipmi_address'].value() or
                    self.fields['ssh_address'].value())
        except AttributeError:
            # when the field is not bound
            name = _("Undefined node")
        return name

    def create_node(self, request, data):
        kwargs = get_driver_info_dict(data)
        kwargs.update(
            cpu_arch=data.get('cpu_arch'),
            cpus=data.get('cpus'),
            memory_mb=data.get('memory_mb'),
            local_gb=data.get('local_gb'),
            mac_addresses=data['mac_addresses'].split(),
        )
        api.node.Node.create(request, **kwargs)

    def handle(self, request, data):
        success = True
        data = self.cleaned_data
        try:
            self.create_node(request, data)
        except Exception:
            success = False
            exceptions.handle(request, _('Unable to register node.'))
            # TODO(tzumainn) If there is a failure between steps, do we
            # have to unregister nodes, delete ports, etc?
        return success


class RegisterNodeForm(BaseNodeForm):
    mac_addresses = tuskar_ui.forms.MultiMACField(
        label=_("NIC MAC Addresses"),
        widget=django.forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '2',
        }),
    )
    cpu_arch = django.forms.ChoiceField(
        label=_("Architecture"),
        required=True,
        choices=CPU_ARCH_CHOICES,
        widget=django.forms.Select(
            attrs={'class': 'form-control'}),
    )
    cpus = django.forms.IntegerField(
        label=_("CPUs"),
        required=True,
        min_value=1,
        initial=1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'form-control'}),
    )
    memory_mb = django.forms.IntegerField(
        label=_("Memory"),
        required=True,
        min_value=1,
        initial=1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'form-control'}),
    )
    local_gb = django.forms.IntegerField(
        label=_("Local Disk"),
        required=True,
        min_value=1,
        initial=1,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'class': 'form-control'}),
    )


class AutoDiscoverNodeForm(BaseNodeForm):
    mac_addresses = tuskar_ui.forms.MultiMACField(
        label=_("NIC MAC Addresses"),
        required=False,
        widget=django.forms.Textarea(attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-pxe_ssh': _("PXE + SSH"),
            'rows': 2,
        }),
    )

    def create_node(self, request, data):
        kwargs = get_driver_info_dict(data)
        kwargs.update(
            mac_addresses=data['mac_addresses'].split(),
        )
        auto_discover_node(request, kwargs)


class BaseNodeFormset(tuskar_ui.forms.SelfHandlingFormset):

    def clean(self):
        for form in self:
            if not form.cleaned_data:
                raise django.forms.ValidationError(
                    _("Please provide node data for all nodes."))
            if not form.cleaned_data.get('ipmi_username'):
                form.cleaned_data['ipmi_username'] = None
            if not form.cleaned_data.get('ipmi_password'):
                form.cleaned_data['ipmi_password'] = None


RegisterNodeFormset = django.forms.formsets.formset_factory(
    RegisterNodeForm, extra=1,
    formset=BaseNodeFormset)


AutoDiscoverNodeFormset = django.forms.formsets.formset_factory(
    AutoDiscoverNodeForm, extra=1,
    formset=BaseNodeFormset)


class AutoDiscoverCSVNodeForm(forms.SelfHandlingForm):
    csv_file = forms.FileField(label=_("CSV File"),
                               required=False)

    def handle(self, request, data):
        success = True
        all_node_data = csv.reader(data['csv_file'])
        for node_data in all_node_data:
            driver = node_data[0]
            kwargs = {
                'driver': driver
            }
            if driver == 'pxe_ssh':
                kwargs.update(
                    ssh_address=node_data[1],
                    ssh_username=node_data[2],
                    ssh_key_contents=node_data[3],
                    mac_addresses=node_data[4].split()
                )
            else:
                kwargs.update(
                    ipmi_address=node_data[1],
                    ipmi_username=node_data[2],
                    ipmi_password=node_data[3],
                )

            try:
                auto_discover_node(request, kwargs)
            except Exception:
                success = False
                exceptions.handle(request, _('Unable to register node.'))
                # TODO(tzumainn) If there is a failure between steps, do we
                # have to unregister nodes, delete ports, etc?

        return success
