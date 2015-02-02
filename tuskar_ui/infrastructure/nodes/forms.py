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
    ('', _("unspecified")),
    ('amd64', _("amd64")),
    ('x86', _("x86")),
    ('x86_64', _("x86_64")),
]
DRIVER_CHOICES = [
    ('pxe_ipmitool', _("IPMI Driver")),
    ('pxe_ssh', _("PXE + SSH")),
]


def get_driver_info_dict(data):
    driver = data['driver']
    driver_dict = {'driver': driver}
    if driver == 'pxe_ipmitool':
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


def create_node(request, data):
    cpu_arch = data.get('cpu_arch')
    cpus = data.get('cpus')
    memory_mb = data.get('memory_mb')
    local_gb = data.get('local_gb')

    kwargs = get_driver_info_dict(data)
    kwargs.update(
        cpu_arch=cpu_arch,
        cpus=cpus,
        memory_mb=memory_mb,
        local_gb=local_gb,
        mac_addresses=data['mac_addresses'].split(),
    )
    node = api.node.Node.create(request, **kwargs)

    # If not all the parameters have been filled in, run the autodiscovery
    if not all([cpu_arch, cpus, memory_mb, local_gb]):
        api.node.Node.set_maintenance(request, node.uuid, True)
        api.node.Node.discover(request, [node.uuid])


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
            'data-driver-pxe_ipmitool': _("IPMI Driver"),
        }),
    )
    ipmi_username = django.forms.CharField(
        label=_("IPMI User"),
        required=False,
        widget=django.forms.TextInput(attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-pxe_ipmitool': _("IPMI Driver"),
        }),
    )
    ipmi_password = django.forms.CharField(
        label=_("IPMI Password"),
        required=False,
        widget=django.forms.PasswordInput(render_value=True, attrs={
            'class': 'form-control switched',
            'data-switch-on': 'driver',
            'data-driver-pxe_ipmitool': _("IPMI Driver"),
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
    mac_addresses = tuskar_ui.forms.MultiMACField(
        label=_("NIC MAC Addresses"),
        required=True,
        widget=django.forms.Textarea(attrs={
            'placeholder': _('unspecified'),
            'rows': '2',
        }),
    )
    cpu_arch = django.forms.ChoiceField(
        label=_("Architecture"),
        required=False,
        choices=CPU_ARCH_CHOICES,
        widget=django.forms.Select(
            attrs={'placeholder': _('unspecified')}),
    )
    cpus = django.forms.IntegerField(
        label=_("CPUs"),
        required=False,
        min_value=0,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'placeholder': _('unspecified')}),
    )
    memory_mb = django.forms.IntegerField(
        label=_("Memory"),
        required=False,
        min_value=0,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'placeholder': _('unspecified')}),
    )
    local_gb = django.forms.IntegerField(
        label=_("Local Disk"),
        required=False,
        min_value=0,
        widget=tuskar_ui.forms.NumberInput(
            attrs={'placeholder': _('unspecified')}),
    )

    def get_name(self):
        try:
            name = (self.fields['ipmi_address'].value() or
                    self.fields['ssh_address'].value())
        except AttributeError:
            # when the field is not bound
            name = _("Undefined node")
        return name

    def handle(self, request, data):
        success = True
        try:
            create_node(request, data)
        except Exception:
            success = False
            exceptions.handle(request, _('Unable to register node.'))
            # TODO(tzumainn) If there is a failure between steps, do we
            # have to unregister nodes, delete ports, etc?
        return success

    def clean_ipmi_username(self):
        return self.cleaned_data.get('ipmi_username') or None

    def clean_ipmi_password(self):
        return self.cleaned_data.get('ipmi_password') or None


class BaseNodeFormset(tuskar_ui.forms.SelfHandlingFormset):
    def clean(self):
        for form in self:
            if not form.cleaned_data:
                raise django.forms.ValidationError(
                    _("Please provide node data for all nodes."))


class UploadNodeForm(forms.SelfHandlingForm):
    csv_file = forms.FileField(label=_("CSV File"), required=True)

    def handle(self, request, data):
        return True

    def get_data(self):
        data = []
        for row in csv.reader(self.cleaned_data['csv_file']):
            driver = row[0].strip()
            if driver == 'pxe_ssh':
                node = dict(
                    ssh_address=row[1],
                    ssh_username=row[2],
                    ssh_key_contents=row[3],
                    mac_addresses=row[4],
                    driver=driver,
                )
            elif driver == 'pxe_ipmitool':
                node = dict(
                    ipmi_address=row[1],
                    ipmi_username=row[2],
                    ipmi_password=row[3],
                    driver=driver,
                )
            data.append(node)
        return data


RegisterNodeFormset = django.forms.formsets.formset_factory(
    NodeForm, extra=1, formset=BaseNodeFormset)
