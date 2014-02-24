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
import horizon.exceptions
import horizon.forms
import horizon.messages

from tuskar_ui import api


class UndeployOvercloud(horizon.forms.SelfHandlingForm):
    def handle(self, request, data):
        try:
            api.Overcloud.delete(request, self.initial['overcloud_id'])
        except Exception:
            horizon.exceptions.handle(request,
                                      _("Unable to undeploy overcloud."))
            return False
        else:
            msg = _('Undeployment in progress.')
            horizon.messages.success(request, msg)
            return True


# TODO(rdopieralski) Get the list of flavors
def get_flavors():
    yield (None, '----')
    yield ('xxx', 'Some Hardware Profile')
    yield ('yyy', 'Other Hardware Profile')


class OvercloudRoleForm(horizon.forms.SelfHandlingForm):
    id = django.forms.IntegerField(
        widget=django.forms.HiddenInput)
    name = django.forms.CharField(
        label=_("Name"), required=False,
        widget=django.forms.TextInput(
            attrs={'readonly': 'readonly', 'disabled': 'disabled'}))
    description = django.forms.CharField(
        label=_("Description"), required=False,
        widget=django.forms.Textarea(
            attrs={'readonly': 'readonly', 'disabled': 'disabled'}))
    image_name = django.forms.CharField(
        label=_("Image"), required=False,
        widget=django.forms.TextInput(
            attrs={'readonly': 'readonly', 'disabled': 'disabled'}))
    flavor_id = django.forms.ChoiceField(
        label=_("Node Profile"), required=False, choices=get_flavors())

    def handle(self, request, context):
        # TODO(rdopieralski) Associate the flavor with the role
        return True
