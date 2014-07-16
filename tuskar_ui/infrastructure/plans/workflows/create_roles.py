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

import tuskar_ui.workflows
from tuskar_ui.infrastructure.plans import tables

import django.forms
from django.utils.translation import ugettext_lazy as _
import horizon.workflows


class Action(horizon.workflows.Action):
    class Meta:
        name = _("Setup Roles")

    def clean(self):
        cleaned_data = super(Action, self).clean()
        table = self.initial.get('_tables', {}).get('setup_roles')
        if table:
            formset = table.get_formset()
            if formset.is_valid():
                cleaned_data['setup_roles'] = [
                    (
                        form.cleaned_data['name'],
                        form.cleaned_data['description'],
                        form.cleaned_data['image_name'],
                        form.cleaned_data['flavor_id'],
                    ) for form in formset if form.cleaned_data
                ]
            else:
                raise django.forms.ValidationError(
                    _('Errors in the roles setup.')
                )
        return cleaned_data


class Step(tuskar_ui.workflows.TableStep):
    table_classes = (
        tables.PlanRolesTable,
    )
    contributes = (
        'setup_roles',
    )
    template_name = 'infrastructure/plans/create_roles.html'
    action_class = Action

    def get_setup_roles_data(self):
        return []

    def contribute(self, data, context):
        context.update(data)
        return context
