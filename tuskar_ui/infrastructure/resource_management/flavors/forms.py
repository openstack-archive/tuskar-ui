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

from openstack_dashboard import api


class CreateFlavor(forms.SelfHandlingForm):
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
        cleaned_data = super(CreateFlavor, self).clean()
        name = cleaned_data.get('name')
        flavor_id = self.initial.get('flavor_id', None)
        try:
            flavors = api.tuskar.FlavorTemplate.list(self.request)
        except:
            flavors = []
            msg = _('Unable to get flavor list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise
        # Check if there is no flavor with the same name
        for flavor in flavors:
            if flavor.name == name and flavor.id != flavor_id:
                raise forms.ValidationError(
                    _('The name "%s" is already used by another flavor.')
                    % name
                )
        return cleaned_data

    def handle(self, request, data):
        try:
            api.tuskar.FlavorTemplate.create(
                request,
                data['name'],
                data['cpu'],
                data['memory'],
                data['storage'],
                data['ephemeral_disk'],
                data['swap_disk']
            )
            msg = _('Created flavor "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to create flavor."))


class EditFlavor(CreateFlavor):

    def handle(self, request, data):
        try:
            api.tuskar.FlavorTemplate.update(
                self.request,
                self.initial['flavor_id'],
                data['name'],
                data['cpu'],
                data['memory'],
                data['storage'],
                data['ephemeral_disk'],
                data['swap_disk']
            )

            msg = _('Updated flavor "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to update flavor."))
