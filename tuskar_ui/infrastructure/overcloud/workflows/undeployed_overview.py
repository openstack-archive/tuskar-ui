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
from horizon.utils import memoized
import horizon.workflows

from tuskar_ui import api
import tuskar_ui.forms


def get_role_id_and_profile_id_from_field_name(field_name):
    """Extract the ids of overcloud role and node profile from the field
    name.
    """
    _count, role_id, profile_id = field_name.split('__', 2)
    return role_id, profile_id


def get_field_name_from_role_id_and_profile_id(role_id, profile_id=''):
    """Compose the ids of overcloud role and node profile into a field name."""
    return 'count__%s__%s' % (role_id, profile_id)


class Action(horizon.workflows.Action):
    class Meta:
        slug = 'undeployed_overview'
        name = _("Overview")

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        for role in self._get_roles():
            if role.name == 'Controller':
                initial = 1
                attrs = {'readonly': 'readonly'}
            else:
                initial = 0
                attrs = {}
            # TODO(rdopieralski) Get a list of hardware profiles for each
            # role here.
            profiles = [(_("Default"), 'default')]
            if not profiles:
                name = get_field_name_from_role_id_and_profile_id(str(role.id))
                attrs = {'readonly': 'readonly'}
                self.fields[name] = django.forms.IntegerField(
                    label='', initial=initial, min_value=initial,
                    widget=tuskar_ui.forms.NumberPickerInput(attrs=attrs))
            for label, profile in profiles:
                name = get_field_name_from_role_id_and_profile_id(
                    str(role.id), profile)
                self.fields[name] = django.forms.IntegerField(
                    label=label, initial=initial, min_value=initial,
                    widget=tuskar_ui.forms.NumberPickerInput(attrs=attrs))

    def roles_fieldset(self):
        """Iterates over lists of fields for each role."""
        for role in self._get_roles():
            yield (
                role.id,
                role.name,
                list(tuskar_ui.forms.fieldset(
                    self, prefix=get_field_name_from_role_id_and_profile_id(
                        str(role.id)))),
            )

    @memoized.memoized
    def _get_roles(self):
        """Retrieve the list of all overcloud roles."""
        return api.OvercloudRole.list(self.request)

    def clean(self):
        for key, value in self.cleaned_data.iteritems():
            if not key.startswith('count_'):
                continue
            role_id, profile = get_role_id_and_profile_id_from_field_name(key)
            if int(value) and not profile:
                raise django.forms.ValidationError(
                    _("Can't deploy nodes without a node profile assigned."))
        return self.cleaned_data


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ('role_counts',)
    template_name = 'infrastructure/overcloud/undeployed_overview.html'
    help_text = _("Nothing deployed yet. Design your first deployment.")

    def get_free_nodes(self):
        """Get the count of nodes that are not assigned yet."""
        return len(api.Node.list(self.workflow.request, False))

    def contribute(self, data, context):
        counts = {}
        for key, value in data.iteritems():
            if not key.startswith('count_'):
                continue
            count, role_id, profile = key.split('__', 2)
            counts[role_id, profile] = int(value)
        context['role_counts'] = counts
        return context
