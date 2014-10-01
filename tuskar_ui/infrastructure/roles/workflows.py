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
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import workflows
from openstack_dashboard.api import glance

from tuskar_ui import api
from tuskar_ui import forms as tuskar_forms
from tuskar_ui.infrastructure.flavors import utils


class UpdateRoleInfoAction(workflows.Action):
    name = forms.CharField(
        label=_("Name"),
        widget=tuskar_forms.LabelWidget(),
        required=False,
    )

    description = forms.CharField(
        label=_("Description"),
        widget=tuskar_forms.LabelWidget(),
        required=False,
    )

    flavor = forms.ChoiceField(
        label=_("Flavor"),
    )

    image = forms.ChoiceField(
        label=_("Image"),
    )

    class Meta:
        name = _("Role Information")
        help_text = _("helptext here")
        slug = 'update_role_info'
        help_text = _("Edit the role details.")

    def __init__(self, request, context, *args, **kwargs):
        super(UpdateRoleInfoAction, self).__init__(request, context, *args,
                                                   **kwargs)
        if not utils.matching_deployment_mode():
            del self.fields['flavor']

    def populate_flavor_choices(self, request, context):
        flavors = api.flavor.Flavor.list(self.request)
        choices = [(f.name, f.name) for f in flavors]
        return [('', _('Unknown'))] + choices

    def populate_image_choices(self, request, context):
        images = glance.image_list_detailed(self.request)[0]
        choices = [(i.id, i.name) for i in images]
        return [('', _('Unknown'))] + choices


class UpdateRoleInfo(workflows.Step):
    action_class = UpdateRoleInfoAction
    depends_on = ("role_id",)
    contributes = ("name", "flavor", "image",)


class UpdateRole(workflows.Workflow):
    slug = "update_role"
    finalize_button_name = _("Save")
    success_message = _('Modified role "%s".')
    failure_message = _('Unable to modify role "%s".')
    index_url = "horizon:infrastructure:roles:index"
    default_steps = (UpdateRoleInfo,)
    success_url = reverse_lazy(
        'horizon:infrastructure:roles:index')

    def name(self):
        # Use context_seed here, as context['name'] returns empty
        # as it's one of the fields.
        return _('Edit Role "%s"') % self.context_seed['name']

    def format_status_message(self, message):
        # Use context_seed here, as context['name'] returns empty
        # as it's one of the fields.
        return message % self.context_seed['name']

    def handle(self, request, data):
        # save it!
        role_id = data['role_id']
        try:
            # Get initial role information
            plan = api.tuskar.Plan.get_the_plan(self.request)
            role = api.tuskar.Role.get(self.request, role_id)
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve role details.'),
                redirect=reverse_lazy(self.index_url))

        parameters = {role.image_id_parameter_name: data['image']}
        if utils.matching_deployment_mode():
            parameters[role.flavor_parameter_name] = data['flavor']

        plan.patch(request, plan.uuid, parameters)
        # success
        return True
