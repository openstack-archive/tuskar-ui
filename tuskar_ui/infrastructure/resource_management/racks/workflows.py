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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

from tuskar_ui import api as tuskar


class NodeCreateAction(workflows.Action):
    # node_macs = forms.CharField(label=_("MAC Addresses"),
    #     widget=forms.Textarea(attrs={'rows': 12, 'cols': 20}),
    #     required=False)

    node_name = forms.CharField(label="Name", required=True)
    prov_mac_address = forms.CharField(label=("MAC Address"),
                                  required=True)

    # Hardware Specifications
    cpus = forms.CharField(label="CPUs", required=True)
    memory_mb = forms.CharField(label="Memory", required=True)
    local_gb = forms.CharField(label="Local Disk (GB)", required=True)

    # Power Management
    pm_address = forms.CharField(label="Power Management IP", required=False)
    pm_user = forms.CharField(label="Power Management User", required=False)
    pm_password = forms.CharField(label="Power Management Password",
                                      required=False,
                                      widget=forms.PasswordInput(
                                          render_value=False))

    # Access
    terminal_port = forms.CharField(label="Terminal Port", required=False)

    class Meta:
        name = _("Nodes")


# mawagner FIXME - For the demo, all we can really do is edit the one
# associated node. That's very much _not_ what this form is actually
# about, though.
class NodeEditAction(NodeCreateAction):

    class Meta:
        name = _("Nodes")

    # FIXME: mawagner - This is all for debugging. The idea is to fetch
    # the first node and display it in the form; the latter part needs
    # implementation. This also needs error handling; right now for testing
    # I want to let it fail, but don't commit like that! :)
    def __init__(self, request, *args, **kwargs):
        super(NodeEditAction, self).__init__(request, *args, **kwargs)
        # TODO(Resolve node edits)
        #rack_id = self.initial['rack_id']
        #rack = tuskar.Rack.get(request, rack_id)
        #nodes = rack.list_nodes


class RackCreateInfoAction(workflows.Action):
    name = forms.RegexField(label=_("Name"),
                            max_length=25,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _('Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')})
    location = forms.CharField(label=_("Location"))
    # see GenericIPAddressField, but not for subnets:
    subnet = forms.CharField(label=_("IP Subnet"))
    resource_class_id = forms.ChoiceField(label=_("Resource Class"))

    def clean(self):
        cleaned_data = super(RackCreateInfoAction, self).clean()
        name = cleaned_data.get('name')
        rack_id = self.initial.get('rack_id', None)
        subnet = cleaned_data.get('subnet')
        try:
            racks = tuskar.Rack.list(self.request)
        except Exception:
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
                    _('The subnet is already assigned to rack %s.')
                    % (rack.name))

        return cleaned_data

    def __init__(self, request, *args, **kwargs):
        super(RackCreateInfoAction, self).__init__(request, *args, **kwargs)
        resource_class_id_choices = [('', _("Select a Resource Class"))]
        for rc in tuskar.ResourceClass.list(request):
            resource_class_id_choices.append((rc.id, rc.name))
        self.fields['resource_class_id'].choices = resource_class_id_choices

    class Meta:
        name = _("Rack Settings")


class CreateRackInfo(workflows.Step):
    action_class = RackCreateInfoAction

    contributes = ('name', 'resource_class_id', 'subnet', 'location')

    def get_racks_data():
        pass


class EditRackInfo(CreateRackInfo):
    depends_on = ('rack_id',)


class CreateNodes(workflows.Step):
    action_class = NodeCreateAction
    contributes = ('node_name', 'prov_mac_address', 'cpus', 'memory_mb',
                   'local_gb', 'pm_address', 'pm_user', 'pm_password',
                   'terminal_port')

    def get_nodes_data():
        pass


class EditNodes(CreateNodes):
    action_class = NodeEditAction
    depends_on = ('rack_id',)
    contributes = ('node_macs',)
    # help_text = _("Editing nodes via textbox is not presently supported.")


class CreateRack(workflows.Workflow):
    default_steps = (CreateRackInfo, CreateNodes)
    slug = "create_rack"
    name = _("Add Rack")
    success_url = 'horizon:infrastructure:resource_management:index'
    success_message = _("Rack created.")
    failure_message = _("Unable to create rack.")

    def handle(self, request, data):
        try:
            if data['node_name'] is not None:
                node = tuskar.Node.create(
                    request, data['node_name'],
                    data['cpus'], data['memory_mb'],
                    data['local_gb'], data['prov_mac_address'],
                    data['pm_address'], data['pm_user'],
                    data['pm_password'], data['terminal_port'])
            if node:
                node_id = node.id
            else:
                node_id = None

            # Then, register the Rack, including the node if it exists
            tuskar.Rack.create(request, data['name'],
                                   data['resource_class_id'],
                                   data['location'],
                                   data['subnet'],
                                   [{'id': node_id}])

            return True
        except Exception:
            exceptions.handle(request, _("Unable to create rack."))


class EditRack(CreateRack):
    default_steps = (EditRackInfo, EditNodes)
    slug = "edit_rack"
    name = _("Edit Rack")
    success_url = 'horizon:infrastructure:resource_management:index'
    success_message = _("Rack updated.")
    failure_message = _("Unable to update rack.")

    def handle(self, request, data):
        try:
            rack_id = self.context['rack_id']
            tuskar.Rack.update(request, rack_id, data)
            return True
        except Exception:
            exceptions.handle(request, _("Unable to update rack."))


class DetailEditRack(EditRack):
    success_url = 'horizon:infrastructure:resource_management:racks:detail'

    def get_success_url(self):
        rack_id = self.context['rack_id']
        return reverse(self.success_url, args=(rack_id,))

    def get_failure_url(self):
        rack_id = self.context['rack_id']
        return reverse(self.success_url, args=(rack_id,))
