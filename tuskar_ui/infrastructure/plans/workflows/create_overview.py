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

from django.utils.translation import ugettext_lazy as _
from horizon import forms
from horizon.utils import memoized
import horizon.workflows
from openstack_dashboard import api as horizon_api

from tuskar_ui import api
import tuskar_ui.forms


class Action(horizon.workflows.Action):
    
    role_ids = forms.MultipleChoiceField(
        label=_("Roles"),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Select roles for this plan."))

    class Meta:
        slug = 'create_overview'
        name = _("Overview")

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)

        role_ids_choices = []
        roles = api.tuskar.OvercloudRole.list(self.request)
        for r in roles:
            role_ids_choices.append((r.id, r.name))
        self.fields['role_ids'].choices = sorted(
            role_ids_choices)
            
    def clean(self):
        for key, value in self.cleaned_data.iteritems():
            if not key.startswith('count_'):
                continue
            role_id, flavor = get_role_id_and_flavor_id_from_field_name(key)
            if int(value) and not flavor:
                raise django.forms.ValidationError(
                    _("Can't deploy nodes without a flavor assigned."))
        return self.cleaned_data


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ('role_ids',)
    template_name = 'infrastructure/plans/create_overview.html'
    help_text = _("Nothing deployed yet. Design your first deployment.")

    def contribute(self, data, context):
        context = super(Step, self).contribute(data, context)
        return context
