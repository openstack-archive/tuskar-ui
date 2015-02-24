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
import django.forms
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import workflows
from openstack_dashboard.api import glance

from tuskar_ui import api
import tuskar_ui.forms
from tuskar_ui.infrastructure.flavors import utils
from tuskar_ui.infrastructure.parameters import forms as parameters_forms
from tuskar_ui.utils import utils as tuskar_utils


class UpdateRoleInfoAction(workflows.Action):
    # TODO(rdopiera) Make the name and description editable.
    name = forms.CharField(
        label=_("Name"),
        required=False,
        widget=tuskar_ui.forms.StaticTextWidget
    )
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=tuskar_ui.forms.StaticTextWidget
    )
    flavor = forms.ChoiceField(
        label=_("Flavor"),
    )
    image = forms.ChoiceField(
        label=_("Image"),
    )
    nodes = forms.IntegerField(
        label=_("Number of Nodes"),
        required=False,
        initial=0,
    )

    class Meta(object):
        name = _("Overall Settings")
        slug = 'update_role_info'
        help_text = _("Edit the role details.")

    def __init__(self, request, context, *args, **kwargs):
        super(UpdateRoleInfoAction, self).__init__(request, context, *args,
                                                   **kwargs)
        self.available_nodes = context['available_nodes']
        self.fields['nodes'].widget = tuskar_ui.forms.NumberInput(attrs={
            'min': 0,
            'max': self.available_nodes,
        })
        self.fields['nodes'].help_text = _(
            "{0} nodes available").format(self.available_nodes)
        if not utils.matching_deployment_mode():
            del self.fields['flavor']

    def populate_flavor_choices(self, request, context):
        flavors = api.flavor.Flavor.list(self.request)
        choices = [(f.name, f.name) for f in flavors]
        return [('', _('Unknown'))] + choices

    def populate_image_choices(self, request, context):
        images = glance.image_list_detailed(self.request)[0]
        images = [image for image in images
                  if tuskar_utils.check_image_type(image,
                                                   'overcloud provisioning')]
        choices = [(i.id, i.name) for i in images]
        return [('', _('Unknown'))] + choices

    def clean_nodes(self):
        new_count = int(self.cleaned_data['nodes'] or 0)
        if new_count > self.available_nodes:
            raise django.forms.ValidationError(_(
                "There are only {0} nodes available "
                "for the selected flavor."
            ).format(self.available_nodes))
        return str(new_count)

    def handle(self, request, context):
        return {
            'name': self.cleaned_data['name'],
            'description': self.cleaned_data['description'],
            'flavor': self.cleaned_data.get('flavor'),
            'image': self.cleaned_data['image'],
            'nodes': self.cleaned_data['nodes'],
        }


class UpdateRoleConfigAction(workflows.Action):
    class Meta(object):
        name = _("Service Configuration")
        slug = 'update_role_config'
        help_text = _("Edit the role's services configuration.")

    def __init__(self, request, context, *args, **kwargs):
        super(UpdateRoleConfigAction, self).__init__(request, context,
                                                     *args, **kwargs)
        self.fields.update(
            parameters_forms.parameter_fields(
                request,
                prefix='%s-1::' % context['name']),
        )

    def handle(self, request, context):
        return {'parameters': self.cleaned_data}


class UpdateRoleInfo(workflows.Step):
    action_class = UpdateRoleInfoAction
    depends_on = ("role_id", "available_nodes")
    contributes = ("name", "description", "flavor", "image", "nodes")
    template_name = 'infrastructure/roles/info.html'


class UpdateRoleConfig(workflows.Step):
    action_class = UpdateRoleConfigAction
    depends_on = ("role_id", "name")
    contributes = ("parameters",)
    template_name = 'infrastructure/roles/config.html'


class UpdateRole(workflows.Workflow):
    slug = "update_role"
    finalize_button_name = _("Save")
    success_message = _('Modified role "%s".')
    failure_message = _('Unable to modify role "%s".')
    index_url = "horizon:infrastructure:roles:index"
    default_steps = (
        UpdateRoleInfo,
        UpdateRoleConfig,
    )
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

        parameters = data['parameters']
        parameters[role.image_id_parameter_name] = data['image']
        parameters[role.node_count_parameter_name] = data['nodes']
        if utils.matching_deployment_mode():
            parameters[role.flavor_parameter_name] = data['flavor']

        plan.patch(request, plan.uuid, parameters)
        # TODO(rdopiera) Find out how to update role's name and description.
        return True
