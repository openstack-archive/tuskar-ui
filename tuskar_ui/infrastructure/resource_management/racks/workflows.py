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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import workflows

import requests

from tuskar_ui import api as tuskar
from tuskar_ui import forms as tuskar_forms
from tuskar_ui.infrastructure.resource_management.nodes import tables \
    as nodes_tables
import tuskar_ui.workflows


class RackCreateInfoAction(workflows.Action):
    name = forms.RegexField(label=_("Name"),
                            max_length=25,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _(
                                'Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')})
    location = forms.CharField(label=_("Location"))
    subnet = tuskar_forms.NetworkField(label=_("IP Subnet"))
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


class NodeCreateAction(workflows.Action):
    class Meta:
        name = _("Create Nodes")
        help_text = _("Here you can create the nodes for this rack.")

    def clean(self):
        cleaned_data = super(NodeCreateAction, self).clean()
        table = self.initial.get('_tables', {}).get('nodes')
        if table:
            formset = table.get_formset()
            if formset.is_valid():
                cleaned_data['nodes'] = [
                    form.cleaned_data for form in formset
                    if form.cleaned_data
                    and not form.cleaned_data.get('DELETE')]
            else:
                raise forms.ValidationError(_("Errors in the nodes list."))
        return cleaned_data


class NodeEditAction(NodeCreateAction):
    class Meta:
        name = _("Edit Nodes")
        help_text = _("Here you can edit the nodes for this rack.")


class CreateNodes(tuskar_ui.workflows.TableStep):
    action_class = NodeCreateAction
    contributes = ('nodes',)
    table_classes = (nodes_tables.NodesFormsetTable,)
    template_name = (
        'infrastructure/resource_management/racks/_rack_nodes_step.html')

    def get_nodes_data(self):
        return []


class EditNodes(CreateNodes):
    action_class = NodeEditAction
    depends_on = ('rack_id',)

    def get_nodes_data(self):
        rack_id = self.workflow.context['rack_id']
        rack = tuskar.Rack.get(self.workflow.request, rack_id)
        return rack.list_baremetal_nodes


class CreateRack(workflows.Workflow):
    default_steps = (CreateRackInfo, CreateNodes)
    slug = "create_rack"
    name = _("Add Rack")
    success_url = 'horizon:infrastructure:resource_management:index'
    success_message = _("Rack created.")
    failure_message = _("Unable to create rack.")

    # FIXME active tabs coflict
    # When on page with tabs, the workflow with more steps is used,
    # there is a conflict of active tabs and it always shows the
    # first tab after an action. So I explicitly specify to what
    # tab it should redirect after action, until the coflict will
    # be fixed in Horizon.
    def get_index_url(self):
        """This URL is used both as success and failure URL."""
        return "%s?tab=resource_management_tabs__racks_tab" %\
            urlresolvers.reverse('horizon:infrastructure:resource_management:'
                                 'index')

    def get_success_url(self):
        return self.get_index_url()

    def get_failure_url(self):
        return self.get_index_url()

    def create_or_update_baremetal_node(self, baremetal_node_data):
        """Creates (if id=='') or updates (otherwise) a baremetal node."""
        if baremetal_node_data['id'] not in ('', None):
            baremetal_node_id = unicode(baremetal_node_data['id'])
            # TODO(rdopieralski) there is currently no way to update
            # a baremetal node
            #
            # tuskar.BaremetalNode.update(
            #    self.request,
            #    node_id=node_id,
            #    service_host=baremetal_node_data['service_host'],
            #    cpus=baremetal_node_data['cpus'],
            #    memory_mb=baremetal_node_data['memory_mb'],
            #    local_gb=baremetal_node_data['local_gb'],
            #    prov_mac_address=baremetal_node_data['mac_address'],
            #    pm_address=baremetal_node_data['pm_address'],
            #    pm_user=baremetal_node_data['pm_user'],
            #    pm_password=baremetal_node_data['pm_password'],
            #    terminal_port=baremetal_node_data['terminal_port'])
            return baremetal_node_id
        else:
            baremetal_node = tuskar.BaremetalNode.create(
                self.request,
                service_host=baremetal_node_data['service_host'],
                cpus=baremetal_node_data['cpus'],
                memory_mb=baremetal_node_data['memory_mb'],
                local_gb=baremetal_node_data['local_gb'],
                prov_mac_address=baremetal_node_data['mac_address'],
                pm_address=baremetal_node_data['pm_address'],
                pm_user=baremetal_node_data['pm_user'],
                pm_password=baremetal_node_data['pm_password'],
                terminal_port=baremetal_node_data['terminal_port'])
            return baremetal_node.id

    def handle(self, request, data):
        # First, create and/or update nodes
        baremetal_node_ids = []
        for baremetal_node_data in data['nodes']:
            try:
                baremetal_node_id = self.create_or_update_baremetal_node(
                    baremetal_node_data)
            except Exception:
                exceptions.handle(self.request, _("Unable to update node."))
                return False
            else:
                # Rack.create takes a list of dicts with BaremetalNode ids
                baremetal_node_ids.append({'id': baremetal_node_id})
        try:
            # Then, register the Rack, including the nodes
            tuskar.Rack.create(
                request, name=data['name'],
                resource_class_id=data['resource_class_id'],
                location=data['location'], subnet=data['subnet'],
                baremetal_nodes=baremetal_node_ids)

            return True
        except requests.ConnectionError:
            messages.error(request,
                           _("Unable to connect to Nova Baremetal. Please "
                             "check your configuration."))
            return False
        except Exception:
            exceptions.handle(request, _("Unable to create rack."))
            return False


class EditRack(CreateRack):
    default_steps = (EditRackInfo, EditNodes)
    slug = "edit_rack"
    name = _("Edit Rack")
    success_url = 'horizon:infrastructure:resource_management:index'
    success_message = _("Rack updated.")
    failure_message = _("Unable to update rack.")

    def handle(self, request, data):
        baremetal_nodes_data = data.pop('nodes')
        baremetal_node_ids = [
            {'id': self.create_or_update_baremetal_node(baremetal_node_data)}
            for baremetal_node_data in baremetal_nodes_data]
        try:
            rack_id = self.context['rack_id']
            data['baremetal_nodes'] = baremetal_node_ids
            tuskar.Rack.update(request, rack_id, data)
            return True
        except Exception:
            exceptions.handle(request, _("Unable to update rack."))
            return False


class DetailEditRack(EditRack):
    success_url = 'horizon:infrastructure:resource_management:racks:detail'

    def get_success_url(self):
        rack_id = self.context['rack_id']
        return urlresolvers.reverse(self.success_url, args=(rack_id,))

    def get_failure_url(self):
        rack_id = self.context['rack_id']
        return urlresolvers.reverse(self.success_url, args=(rack_id,))
