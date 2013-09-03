# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from django.core import urlresolvers
from django.forms import formsets
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages

from tuskar_ui import api as tuskar
from tuskar_ui import forms as tuskar_forms
from tuskar_ui.infrastructure.resource_management.flavor_templates import\
    forms as flavor_templates_forms

import logging

LOG = logging.getLogger(__name__)


class DeleteForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(DeleteForm, self).__init__(request, *args, **kwargs)

        resource_class = self.initial.get('resource_class', None)
        self.command = DeleteCommand(request, resource_class)

    def handle(self, request, data):
        try:
            self.command.execute()

            messages.success(request, self.command.msg)
            return True
        except Exception:
            exceptions.handle(request, _("Unable to delete Resource Class."))


# TODO(this command will be reused in table, so code is not duplicated)
class DeleteCommand(object):
    def __init__(self, request, resource_class):
        self.resource_class = resource_class
        self.request = request
        self.header = (_("Deleting resource class '%s.'")
                       % self.resource_class.name)
        self.msg = ""

    def execute(self):
        try:
            tuskar.ResourceClass.delete(self.request,
                                        self.resource_class.id)
            self.msg = (_('Successfully deleted Class "%s".')
                        % self.resource_class.name)
        except Exception:
            self.msg = _('Failed to delete Class %s') % self.resource_class.id
            LOG.info(self.msg)
            redirect = urlresolvers.reverse(
                            'horizon:infrastructure:resource_management:index')
            exceptions.handle(self.request, self.msg, redirect=redirect)


# Inherit from the EditFlavorTemplate form to get all the nice validation.
class FlavorTemplatesForm(flavor_templates_forms.EditFlavorTemplate):
    def __init__(self, *args, **kwargs):

        # Drop the ``request`` parameter, as Formsets don't support it
        request = None
        super(FlavorTemplatesForm, self).__init__(request, *args, **kwargs)

        # Add a field for selecting the flavors
        selected_field = forms.BooleanField(label='', required=False)
        self.fields.insert(0, 'selected', selected_field)

        # Add nice widget types and classes
        self.fields['name'].widget = forms.TextInput(
            attrs={'class': 'input input-small'},
        )
        for name in ['cpu', 'memory', 'storage', 'ephemeral_disk',
                     'swap_disk']:
            self.fields[name].widget = tuskar_forms.NumberInput(
                    attrs={'class': 'number_input_slim'},
            )

    max_vms = forms.IntegerField(
        label=_("Max. VMs"),
        min_value=0,
        initial=0,
        widget=tuskar_forms.NumberInput(
            attrs={'class': 'number_input_slim'},
        ),
        required=False,
    )
    # Long name as used in the validation of EditFlavorTemplate.
    flavor_template_id = forms.IntegerField(widget=forms.HiddenInput())


FlavorTemplatesFormset = formsets.formset_factory(
    FlavorTemplatesForm,
    extra=0,
)
