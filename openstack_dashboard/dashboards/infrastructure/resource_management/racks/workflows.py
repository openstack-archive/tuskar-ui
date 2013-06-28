# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets

from horizon import exceptions
from horizon import workflows
from horizon import forms

from openstack_dashboard import api

import re


class HostCreateAction(workflows.Action):
    host_macs = forms.CharField(label=_("MAC Addresses"),
        widget=forms.Textarea(attrs={'rows': 12, 'cols': 20}),
        required=False)

    class Meta:
        name = _("Nodes")


class RackCreateInfoAction(workflows.Action):
    name = forms.RegexField(label=_("Name"),
                            max_length=25,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _('Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')})
    resource_class_id = forms.ChoiceField(label=_("Resource Class"))
    location = forms.CharField(label=_("Location"))
    # see GenericIPAddressField, but not for subnets:
    subnet = forms.CharField(label=_("IP Subnet"))

    def clean(self):
        cleaned_data = super(RackCreateInfoAction, self).clean()
        name = cleaned_data.get('name')
        rack_id = self.initial.get('rack_id', None)
        resource_class_id = cleaned_data.get('resource_class_id')
        location = cleaned_data.get('location')
        subnet = cleaned_data.get('subnet')
        try:
            racks = api.management.Rack.list(self.request)
        except:
            racks = []
            exceptions.check_message(['Connection', 'refused'],
                _("Unable to retrieve rack list."))
            raise

        # Validations: detect duplicates
        for rack in racks:
            other_record = rack_id != rack.id
            if rack.name == name and other_record:
                raise forms.ValidationError(
                    _('The name %s is already used by another rack.')
                    % name)
            if rack.subnet == subnet and other_record:
                raise forms.ValidationError(
                    _('The subnet %s is already assigned to rack %s.')
                    % (subnet, rack.name))

        return cleaned_data

    def __init__(self, request, *args, **kwargs):
        super(RackCreateInfoAction, self).__init__(request, *args, **kwargs)
        resource_class_id_choices = [('', _("Select a Resource Class"))]
        for rc in api.management.ResourceClass.list(request):
            resource_class_id_choices.append((rc.id, rc.name))
        self.fields['resource_class_id'].choices = resource_class_id_choices

    class Meta:
        name = _("Rack Settings")


class CreateRackInfo(workflows.Step):
    action_class = RackCreateInfoAction

    contributes = ('name', 'resource_class_id', 'subnet', 'location')

    def get_racks_data():
        pass


class CreateHosts(workflows.Step):
    action_class = HostCreateAction
    contributes = ('host_macs',)

    def get_hosts_data():
        pass


class CreateRack(workflows.Workflow):
    default_steps = (CreateRackInfo, CreateHosts)
    slug = "create_rack"
    name = _("Add Rack")
    success_url = 'horizon:infrastructure:resource_management:index'
    success_message = _("Rack created.")
    failure_message = _("Unable to create rack.")

    def handle(self, request, data):

        try:
            rack = api.management.Rack.create(request, data['name'],
                                              data['resource_class_id'],
                                              data['location'],
                                              data['subnet'])

            if data['host_macs'] is not None:
                hosts = data['host_macs'].splitlines(False)
                api.management.Rack.register_hosts(rack, hosts)

            return True
        except:
            exceptions.handle(request, _("Unable to create rack."))


class EditRack(CreateRack):
    # FIXME: Build out these methods
    # default_steps = (EditRackInfo, EditHosts)
    slug = "edit_rack"
    name = _("Edit Rack")
    success_url = 'horizon:infrastructure:resource_management:index'
    success_message = _("Rack updated.")
    failure_message = _("Unable to update rack.")
