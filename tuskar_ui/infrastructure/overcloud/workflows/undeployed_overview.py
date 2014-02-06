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
import horizon.workflows

import tuskar_ui.forms


ROLES = [
    ('controller', _("Controller")),
    ('compute', _("Compute")),
    ('object_storage', _("Object Storage")),
    ('block_storage', _("Block Storage")),
]


class Action(horizon.workflows.Action):
    class Meta:
        slug = 'undeployed_overview'
        name = _("Overview")

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        for role, label in ROLES:
            # TODO(rdopieralski) Get a list of hardware profiles for each
            # role here.
            name = 'count__%s__%s' % (role, 'default')
            if role == 'controller':
                initial = 1
                self.fields[name] = django.forms.IntegerField(
                    label=_("Default"), initial=initial, min_value=initial,
                    widget=tuskar_ui.forms.NumberPickerInput(attrs={
                        'readonly': 'readonly',
                    }))
            else:
                initial = 0
                self.fields[name] = django.forms.IntegerField(
                    label=_("Default"), initial=initial, min_value=initial,
                    widget=tuskar_ui.forms.NumberPickerInput)

    def roles_fieldset(self):
        for role, label in ROLES:
            yield (
                role,
                label,
                list(tuskar_ui.forms.fieldset(
                    self, prefix='count__%s__' % role)),
            )

    def handle(self, request, context):
        counts = {}
        for key, value in self.cleaned_data.iteritems():
            if not key.startswith('count_'):
                continue
            _count, role, profile = key.split('__', 2)
            counts[role, profile] = int(value)
        context['role_counts'] = counts
        return context


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ('role_counts',)
    template_name = 'infrastructure/overcloud/undeployed_overview.html'
    help_text = _("Nothing deployed yet. Design your first deployment.")

    def get_context_data(self, *args, **kwargs):
        context = super(Step, self).get_context_data(*args, **kwargs)
        context['free_nodes'] = 3
        return context
