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
from horizon import messages

from tuskar_ui import api
import tuskar_ui.forms


DEFAULT_KERNEL_IMAGE_NAME = 'bm-deploy-kernel'
DEFAULT_RAMDISK_IMAGE_NAME = 'bm-deploy-ramdisk'

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
    driver_dict = {'driver': driver,
                   'deployment_kernel': data['deployment_kernel'],
                   'deployment_ramdisk': data['deployment_ramdisk'],
                   }
    if driver == 'pxe_ipmitool':
        driver_dict.update(
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
    success = True
    try:
        node = api.node.Node.create(request, **kwargs)
    except Exception:
        success = False
        exceptions.handle(request, _(u"Unable to register node."))
    else:
        # If not all the parameters have been filled in,
        # run the auto-discovery. Note, that the node has been created,
        # so even if we fail here, we report success.
        if not all([cpu_arch, cpus, memory_mb, local_gb]):
            node_uuid = node.uuid
            try:
                api.node.Node.set_maintenance(request, node_uuid, True)
            except Exception:
                exceptions.handle(request, _(
                    u"Can't set maintenance mode on node {0}."
                ).format(node_uuid))
            else:
                try:
                    api.node.Node.discover(request, [node_uuid])
                except Exception:
                    exceptions.handle(request, _(
                        u"Can't start discovery on node {0}."
                    ).format(node_uuid))
    return success


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
    deployment_kernel = django.forms.ChoiceField(
        label=_("Kernel"),
        required=False,
        choices=[],
        widget=django.forms.Select(),
    )
    deployment_ramdisk = django.forms.ChoiceField(
        label=_("Ramdisk"),
        required=False,
        choices=[],
        widget=django.forms.Select(),
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
        return create_node(request, data)

    def clean_ipmi_username(self):
        return self.cleaned_data.get('ipmi_username') or None

    def clean_ipmi_password(self):
        return self.cleaned_data.get('ipmi_password') or None

    def _require_field(self, field_name, cleaned_data):
        if cleaned_data.get(field_name):
            return
        self._errors[field_name] = self.error_class([_(
            u"This field is required"
        )])

    def clean(self):
        cleaned_data = super(NodeForm, self).clean()
        driver = cleaned_data['driver']

        if driver == 'pxe_ipmitool':
            self._require_field('ipmi_address', cleaned_data)
        elif driver == 'pxe_ssh':
            self._require_field('ssh_address', cleaned_data)
            self._require_field('ssh_username', cleaned_data)
            self._require_field('ssh_key_contents', cleaned_data)

        return cleaned_data


class BaseNodeFormset(tuskar_ui.forms.SelfHandlingFormset):
    def __init__(self, *args, **kwargs):
        self.kernel_images = kwargs.pop('kernel_images')
        self.ramdisk_images = kwargs.pop('ramdisk_images')
        super(BaseNodeFormset, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        deployment_kernel_choices = [(kernel.id, kernel.name)
                                     for kernel in self.kernel_images]
        deployment_ramdisk_choices = [(ramdisk.id, ramdisk.name)
                                      for ramdisk in self.ramdisk_images]
        form.fields['deployment_kernel'].choices = deployment_kernel_choices
        form.fields['deployment_ramdisk'].choices = deployment_ramdisk_choices

    def clean(self):
        all_macs = api.node.Node.get_all_mac_addresses(self.request)
        bad_macs = set()
        bad_macs_error = _("Duplicate MAC addresses submitted: %s.")

        for form in self:
            if not form.cleaned_data:
                raise django.forms.ValidationError(
                    _("Please provide node data for all nodes."))

            new_macs = form.cleaned_data.get('mac_addresses')
            if not new_macs:
                continue
            new_macs = set(new_macs.split())

            # Prevent submitting duplicated MAC addresses
            # or MAC addresses of existing nodes
            bad_macs |= all_macs & new_macs
            all_macs |= new_macs

        if bad_macs:
            raise django.forms.ValidationError(
                bad_macs_error % ", ".join(bad_macs))


class UploadNodeForm(forms.SelfHandlingForm):
    csv_file = forms.FileField(label='', required=False)

    def handle(self, request, data):
        return True

    def get_data(self):
        data = []

        for row in csv.reader(self.cleaned_data['csv_file']):
            try:
                driver = row[0].strip()
            except IndexError:
                messages.error(self.request,
                               _("Unable to parse the CSV file."))
                return []

            if driver in ('pxe_ssh', 'pxe_ipmitool'):
                node_keys = ('mac_addresses', 'cpu_arch', 'cpus', 'memory_mb',
                             'local_gb')

                if driver == 'pxe_ssh':
                    driver_keys = (driver, 'ssh_address', 'ssh_username',
                                   'ssh_key_contents')
                elif driver == 'pxe_ipmitool':
                    driver_keys = (driver, 'ipmi_address', 'ipmi_username',
                                   'ipmi_password')

                node = dict(izip(driver_keys+node_keys, row))

                data.append(node)
            else:
                messages.error(self.request,
                               _("Unknown driver: %s.") % driver)
                return []
        return data


RegisterNodeFormset = django.forms.formsets.formset_factory(
    NodeForm, extra=1, formset=BaseNodeFormset)
