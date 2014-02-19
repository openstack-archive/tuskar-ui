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
from openstack_dashboard import api as horizon_api

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


def get_flavors(request):
    yield '', '----'
    try:
        flavors = horizon_api.nova.flavor_list(request, None)
    except Exception:
        horizon.exceptions.handle(request,
                                  _('Unable to retrieve flavor list.'))
        return
    for flavor in flavors:
        yield flavor.id, flavor.name


class OvercloudRoleForm(horizon.forms.SelfHandlingForm):
    id = django.forms.IntegerField(
        widget=django.forms.HiddenInput)
    name = django.forms.CharField(
        label=_("Name"), required=False,
        widget=django.forms.TextInput(
            attrs={'readonly': 'readonly', 'disbaled': 'disabled'}))
    description = django.forms.CharField(
        label=_("Description"), required=False,
        widget=django.forms.Textarea(
            attrs={'readonly': 'readonly', 'disbaled': 'disabled'}))
    image_name = django.forms.CharField(
        label=_("Image"), required=False,
        widget=django.forms.TextInput(
            attrs={'readonly': 'readonly', 'disbaled': 'disabled'}))
    flavor_id = django.forms.ChoiceField(
        label=_("Node Profile"), required=False, choices=())

    def __init__(self, *args, **kwargs):
        super(OvercloudRoleForm, self).__init__(*args, **kwargs)
        self.fields['flavor_id'].choices = list(get_flavors(self.request))

    def handle(self, request, context):
        try:
            role = api.OvercloudRole.get(request, context['id'])
            role.update(request, flavor_id=context['flavor_id'])
        except Exception:
            horizon.exceptions.handle(request,
                                      _('Unable to update the role.'))
            return False
        return True
