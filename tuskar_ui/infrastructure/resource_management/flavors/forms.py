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

from django.forms import formsets
from django.utils import datastructures
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import forms

from tuskar_ui import forms as tuskar_forms


CAPACITIES = datastructures.SortedDict([
    # (name, (label, unit, required)),
    ('cpu', (_('VCPU'), '', True)),
    ('memory', (_('RAM (MB)'), 'MB', True)),
    ('storage', (_('Root Disk (GB)'), 'GB', True)),
    ('ephemeral_disk', (_('Ephemeral Disk (GB)'), 'GB', False)),
    ('swap_disk', (_('Swap Disk (GB)'), 'GB', False)),
])


class FlavorForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.RegexField(label=_("Name"),
                            max_length=25,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _(
                                'Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')},
                            widget=forms.TextInput(attrs={
                                'class': 'input input-small',
                            }))

    def __init__(self, *args, **kwargs):
        super(FlavorForm, self).__init__(*args, **kwargs)

        for name, (label, unit, required) in CAPACITIES.items():
            self.fields[name] = forms.IntegerField(
                label=label,
                min_value=0,
                required=required,
                widget=tuskar_forms.NumberInput(attrs={
                    'class': 'input number_input_slim',
                }))


class BaseFlavorFormSet(formsets.BaseFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid
            # on its own
            return
        names = {}
        for form in self.forms:
            name = form.cleaned_data.get('name')
            if not name:
                continue
            if name in names:
                message = _("This value repeats, but it should be unique.")
                other_form = names[name]
                form._errors['name'] = form.error_class([message])
                other_form._errors['name'] = other_form.error_class([message])
            names[name] = form


FlavorFormset = formsets.formset_factory(FlavorForm, extra=1, can_delete=True,
                                         formset=BaseFlavorFormSet)
