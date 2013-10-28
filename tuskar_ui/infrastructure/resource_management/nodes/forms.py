# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

import tuskar_ui.forms


class NodeForm(django.forms.Form):
    id = django.forms.IntegerField(
        required=False,
        widget=django.forms.HiddenInput())

    service_host = django.forms.CharField(
        label=_("Service Host"),
        widget=django.forms.TextInput(attrs={'class': 'input input-mini'}),
        required=True)
    mac_address = tuskar_ui.forms.MACField(
        label=_("MAC Address"),
        widget=django.forms.TextInput(attrs={'class': 'input input-mini'}),
        required=True)

    # Hardware Specifications
    cpus = django.forms.IntegerField(
        label=_("CPUs"), required=True,
        min_value=1, widget=tuskar_ui.forms.NumberInput(attrs={
            'class': 'input number_input_slim',
        }))
    memory_mb = django.forms.IntegerField(
        label=_("Memory"), required=True, min_value=1,
        widget=tuskar_ui.forms.NumberInput(attrs={
            'class': 'input number_input_slim',
        }))
    local_gb = django.forms.IntegerField(
        label=_("Local Disk (GB)"), min_value=1,
        widget=tuskar_ui.forms.NumberInput(attrs={
            'class': 'input number_input_slim',
        }), required=True)

    # Power Management
    pm_address = django.forms.GenericIPAddressField(
        widget=django.forms.TextInput(attrs={'class': 'input input-mini'}),
        label=_("Power Management IP"), required=False)
    pm_user = django.forms.CharField(
        label=_("Power Management User"),
        widget=django.forms.TextInput(attrs={'class': 'input input-mini'}),
        required=False)
    pm_password = django.forms.CharField(
        label=_("Power Management Password"),
        required=False, widget=django.forms.PasswordInput(
            render_value=False,
            attrs={'class': 'input input-mini'}))

    # Access
    terminal_port = django.forms.IntegerField(
        label=_("Terminal Port"),
        required=False, min_value=0, max_value=1024,
        widget=tuskar_ui.forms.NumberInput(attrs={
            'class': 'input number_input_slim',
        }))


class BaseNodeFormSet(django.forms.formsets.BaseFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid
            # on its own
            return
        unique_fields = ('mac_address', 'pm_address')
        values = dict((field, {}) for field in unique_fields)
        for form in self.forms:
            for field in unique_fields:
                value = form.cleaned_data.get(field)
                if not value:
                    continue
                if value in values[field]:
                    message = _("This value repeats, but it should be unique.")
                    other_form = values[field][value]
                    form._errors[field] = form.error_class([message])
                    other_form._errors[field] = other_form.error_class(
                        [message])
                values[field][value] = form


NodeFormset = django.forms.formsets.formset_factory(
    NodeForm, extra=1, can_delete=True, formset=BaseNodeFormSet)
