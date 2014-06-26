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

from openstack_dashboard.api import neutron
from tuskar_ui import api
from tuskar_ui import utils


def make_field(name, Type, NoEcho, Default, Description, AllowedValues=None,
               **kwargs):
    """Create a form field using the parameters from a Heat template."""

    label = utils.de_camel_case(name)
    Widget = django.forms.TextInput
    attrs = {}
    widget_kwargs = {}
    if Default == 'unset':
        attrs['placeholder'] = _("auto-generate")
    if Type == 'Json':
        # TODO(lsmola) this should eventually be a textarea
        Field = django.forms.CharField
    else:
        # TODO(lsmola) we should use Horizon code for generating of the form.
        # There it should have list of all supported types according to Heat
        # specification.
        Field = django.forms.CharField

    if NoEcho == 'true':
        Widget = django.forms.PasswordInput
        widget_kwargs['render_value'] = True
    if AllowedValues is not None:
        return django.forms.ChoiceField(initial=Default, choices=[
            (value, value) for value in AllowedValues
        ], help_text=Description, required=False, label=label)
    return Field(widget=Widget(attrs=attrs, **widget_kwargs), initial=Default,
                 help_text=Description, required=False, label=label)


class Action(horizon.workflows.Action):
    class Meta:
        slug = 'deployed_configuration'
        name = _("Configuration")

    def __init__(self, request, *args, **kwargs):
        super(Action, self).__init__(request, *args, **kwargs)
        params = api.tuskar.OvercloudPlan.template_parameters(request).items()
        params.sort()

        for name, data in params:
            # workaround for this parameter, which needs a preset taken from
            # neutron
            if name == 'NeutronControlPlaneID':
                networks = neutron.network_list(request)
                for network in networks:
                    if network.name == 'ctlplane':
                        data['Default'] = network.id
                        break;

            self.fields[name] = make_field(name, **data)

    def clean(self):
        # this is a workaround for a single parameter
        if 'GlanceLogFile' in self.cleaned_data:
            if not self.cleaned_data['GlanceLogFile']:
                self.cleaned_data['GlanceLogFile'] = u"''"
        return self.cleaned_data


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ('configuration',)
    template_name = 'infrastructure/overcloud/undeployed_configuration.html'

    def contribute(self, data, context):
        context['configuration'] = data
        return context
