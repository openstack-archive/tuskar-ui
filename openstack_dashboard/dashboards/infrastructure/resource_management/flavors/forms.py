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

import re

from django.core import validators
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

    def clean_name(self):
        name = self.cleaned_data.get('name')
        try:
            flavors = api.management.flavor_list(self.request)
        except:
            flavors = []
            msg = _('Unable to get flavor list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise
        if flavors is not None:
            for flavor in flavors:
                if flavor.name == name:
                    raise forms.ValidationError(
                      _('The name "%s" is already used by another flavor.')
                      % name
                    )
        return name

    def handle(self, request, data):
        try:
            flavor = api.management.flavor_create(request,
                                                  data['name'])
            msg = _('Created flavor "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to create flavor."))


class EditFlavor(CreateFlavor):
    flavor_id = forms.CharField(widget=forms.widgets.HiddenInput)

    def clean_name(self):
        return self.cleaned_data['name']

    def clean(self):
        cleaned_data = super(EditFlavor, self).clean()
        name = cleaned_data.get('name')
        flavor_id = cleaned_data.get('flavor_id')
        try:
            flavors = api.management.flavor_list(self.request)
        except:
            flavors = []
            msg = _('Unable to get flavor list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise
        # Check if there is no flavor with the same name
        if flavors is not None:
            for flavor in flavors:
                if flavor.name == name and flavor.id != flavor_id:
                    raise forms.ValidationError(
                      _('The name "%s" is already used by another flavor.')
                      % name
                    )
        return cleaned_data

    def handle(self, request, data):
        try:
            flavor_id = data['flavor_id']
            flavor = api.management.flavor_update(
                request, flavor_id, data['name'])
            msg = _('Updated flavor "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to update flavor."))
