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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from tuskar_ui import api as tuskar


class CreateFlavorTemplate(forms.SelfHandlingForm):
    name = forms.RegexField(label=_("Name"),
                            max_length=25,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _('Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')})
    cpu = forms.IntegerField(label=_("VCPU"),
                             min_value=0,
                             initial=0)
    memory = forms.IntegerField(label=_("RAM (MB)"),
                             min_value=0,
                             initial=0)
    storage = forms.IntegerField(label=_("Root Disk (GB)"),
                                 min_value=0,
                                 initial=0)
    ephemeral_disk = forms.IntegerField(label=_("Ephemeral Disk (GB)"),
                                        min_value=0,
                                        initial=0)
    swap_disk = forms.IntegerField(label=_("Swap Disk (MB)"),
                                   min_value=0,
                                   initial=0)

    def clean(self):
        cleaned_data = super(CreateFlavorTemplate, self).clean()
        name = cleaned_data.get('name')
        flavor_template_id = self.initial.get('flavor_template_id', None)
        try:
            flavor_templates = tuskar.FlavorTemplate.list(self.request)
        except:
            flavor_templates = []
            msg = _('Unable to get flavor templates list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise
        # Check if there is no flavor template with the same name
        for flavor_template in flavor_templates:
            if (flavor_template.name == name and
                    flavor_template.id != flavor_template_id):
                raise forms.ValidationError(
                    _('The name "%s" is already used by another'
                      'flavor template.') % name)
        return cleaned_data

    def handle(self, request, data):
        try:
            tuskar.FlavorTemplate.create(
                request,
                data['name'],
                data['cpu'],
                data['memory'],
                data['storage'],
                data['ephemeral_disk'],
                data['swap_disk']
            )
            msg = _('Created Flavor Template "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to create Flavor Template."))


class EditFlavorTemplate(CreateFlavorTemplate):

    def handle(self, request, data):
        try:
            tuskar.FlavorTemplate.update(
                self.request,
                self.initial['flavor_template_id'],
                data['name'],
                data['cpu'],
                data['memory'],
                data['storage'],
                data['ephemeral_disk'],
                data['swap_disk']
            )

            msg = _('Updated Flavor Template "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to update Flavor Template."))
