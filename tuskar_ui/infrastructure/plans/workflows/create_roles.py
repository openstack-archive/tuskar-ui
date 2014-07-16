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

from tuskar_ui import api
from tuskar_ui.infrastructure.plans import forms


class Action(horizon.workflows.Action):
    class Meta:
        slug = 'setup_roles'
        name = _("Setup Roles")

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        initial = [
            {
                'id': role.id,
                'name': role.name,
                'description': role.description,
            } for role in self.get_roles()
        ]
        self.formset = forms.PlanRoleFormSet(
            request=self.request,
            data=self.data or None,
            initial=initial,
        )

    def get_roles(self):
        return api.tuskar.OvercloudRole.list(self.request)

    def clean(self):
        cleaned_data = super(Action, self).clean()
        if self.formset.is_valid():
            cleaned_data['setup_roles'] = [
                form.cleaned_data for form in self.formset
                if form.cleaned_data and not form.cleaned_data.get('DELETE')
            ]
        else:
            raise django.forms.ValidationError(_("Errors in the role setup."))
        return cleaned_data


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = (
        'setup_roles',
    )
    template_name = 'infrastructure/plans/create_roles.html'

    def contribute(self, data, context):
        context = super(Step, self).contribute(data, context)
        context.update(data)
        return context
