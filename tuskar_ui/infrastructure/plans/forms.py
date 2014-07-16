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

import tuskar_ui.api
import tuskar_ui.forms


EMPTY = [('', '----')]


def get_flavor_choices(request):
    try:
        flavors = horizon_api.nova.flavor_list(request, None)
    except Exception:
        horizon.exceptions.handle(request,
                                  _('Unable to retrieve flavor list.'))
        return EMPTY
    return EMPTY + [(flavor.id, flavor.name) for flavor in flavors]


def get_image_choices(request):
    # TODO(rdopieralski) implement
    return EMPTY


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
        label=_("Flavor"), required=False, choices=())

    def __init__(self, *args, **kwargs):
        super(OvercloudRoleForm, self).__init__(*args, **kwargs)
        self.fields['flavor_id'].choices = get_flavor_choices(self.request)

    def handle(self, request, context):
        try:
            role = tuskar_ui.api.tuskar.OvercloudRole.get(
                request, context['id'])
            role.update(request, flavor_id=context['flavor_id'])
        except Exception:
            horizon.exceptions.handle(request,
                                      _('Unable to update the role.'))
            return False
        return True


class PlanRole(django.forms.Form):
    name = django.forms.CharField(
        label=_("Name"), required=True,
    )
    description = django.forms.CharField(
        label=_("Description"), required=False,
        widget=django.forms.Textarea(attrs={
            'rows': 2,
        }),
    )
    image_name = django.forms.ChoiceField(
        label=_("Provisioning Image"), required=True,
        choices=[],
    )
    flavor_id = django.forms.ChoiceField(
        label=_("Flavor"), required=True,
        choices=[],
    )
    size = django.forms.IntegerField(
        label=_("Size"), required=False,
        initial=0,
        widget=tuskar_ui.forms.NumberInput,
    )

    def get_name(self):
        try:
            return self.fields['name'].value()
        except AttributeError:
            # unbound field
            return self.initial.get('name') or _("Unnamed role")


class BasePlanRoleFormset(django.forms.formsets.BaseFormSet):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.flavor_choices = get_flavor_choices(request)
        self.image_choices = get_image_choices(request)
        super(BasePlanRoleFormset, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(BasePlanRoleFormset, self).add_fields(form, index)
        form.fields['flavor_id'].choices = self.flavor_choices
        form.fields['image_name'].choices = self.image_choices


PlanRoleFormSet = django.forms.formsets.formset_factory(
    PlanRole,
    formset=BasePlanRoleFormset,
    extra=0,
)
