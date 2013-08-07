
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

from tuskar_ui import api
import tuskar_ui.workflows

import re

from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.tables import FlavorsTable
from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.tables import RacksTable


class ResourceClassInfoAndFlavorsAction(workflows.Action):
    name = forms.CharField(max_length=255,
                           label=_("Class Name"),
                           help_text="",
                           required=True)
    service_type = forms.ChoiceField(label=_('Class Type'),
                                     required=True,
                                     choices=[('', ''),
                                              ('compute',
                                              ('Compute')),
                                              ('not_compute',
                                              ('Non Compute')),
                                              ],
                                     widget=forms.Select(
                                         attrs={'class': 'switchable'})
                                     )
    image = forms.ChoiceField(label=_('Provisioning Image'),
                              required=True,
                              choices=[('compute-img', ('overcloud-compute'))],
                              widget=forms.Select(
                                attrs={'class': 'switchable'})
                              )

    def clean(self):
        cleaned_data = super(ResourceClassInfoAndFlavorsAction,
                             self).clean()

        name = cleaned_data.get('name')
        resource_class_id = self.initial.get('resource_class_id', None)
        try:
            resource_classes = api.tuskar.ResourceClass.list(self.request)
        except:
            resource_classes = []
            msg = _('Unable to get resource class list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise
        for resource_class in resource_classes:
            if resource_class.name == name and \
                    resource_class_id != resource_class.id:
                raise forms.ValidationError(
                    _('The name "%s" is already used by'
                      ' another resource class.')
                    % name
                )

        return cleaned_data

    class Meta:
        name = _("Class Settings")
        help_text = _("From here you can fill the class "
                      "settings and add flavors to class.")


class CreateResourceClassInfoAndFlavors(tuskar_ui.workflows.TableStep):
    table_classes = (FlavorsTable,)

    action_class = ResourceClassInfoAndFlavorsAction
    template_name = 'infrastructure/resource_management/resource_classes/'\
                    '_resource_class_info_and_flavors_step.html'
    contributes = ("name", "service_type", "flavors_object_ids",
                   'max_vms')

    def contribute(self, data, context):
        request = self.workflow.request
        if data:
            context["flavors_object_ids"] =\
                request.POST.getlist("flavors_object_ids")

            # todo: lsmola django can't parse dictionaruy from POST
            # this should be rewritten to django formset
            context["max_vms"] = {}
            for index, value in request.POST.items():
                match = re.match(
                    '^(flavors_object_ids__max_vms__(.*?))$',
                    index)
                if match:
                    context["max_vms"][match.groups()[1]] = value

        context.update(data)
        return context

    def get_flavors_data(self):
        try:
            resource_class_id = self.workflow.context.get("resource_class_id")
            if resource_class_id:
                resource_class = api.tuskar.ResourceClass.get(
                    self.workflow.request,
                    resource_class_id)

                # TODO(lsmola ugly interface, rewrite)
                self._tables['flavors'].active_multi_select_values = \
                    resource_class.flavortemplates_ids

                all_flavors = resource_class.all_flavors
            else:
                all_flavors = api.tuskar.FlavorTemplate.list(
                        self.workflow.request)
        except Exception:
            all_flavors = []
            exceptions.handle(self.workflow.request,
                              _('Unable to retrieve resource flavors list.'))
        return all_flavors


class RacksAction(workflows.Action):
    class Meta:
        name = _("Racks")


class CreateRacks(tuskar_ui.workflows.TableStep):
    table_classes = (RacksTable,)

    action_class = RacksAction
    contributes = ("racks_object_ids")
    template_name = 'infrastructure/resource_management/'\
                    'resource_classes/_racks_step.html'

    def contribute(self, data, context):
        request = self.workflow.request
        context["racks_object_ids"] =\
            request.POST.getlist("racks_object_ids")

        context.update(data)
        return context

    def get_racks_data(self):
        try:
            resource_class_id = self.workflow.context.get("resource_class_id")
            if resource_class_id:
                resource_class = api.tuskar.ResourceClass.get(
                    self.workflow.request,
                    resource_class_id)
                # TODO(lsmola ugly interface, rewrite)
                self._tables['racks'].active_multi_select_values = \
                    resource_class.racks_ids
                racks = \
                    resource_class.all_racks
            else:
                racks = \
                    api.tuskar.Rack.list(self.workflow.request, True)
        except:
            racks = []
            exceptions.handle(self.workflow.request,
                              _('Unable to retrieve racks list.'))

        return racks


class ResourceClassWorkflowMixin:
    # FIXME active tabs coflict
    # When on page with tabs, the workflow with more steps is used,
    # there is a conflict of active tabs and it always shows the
    # first tab after an action. So I explicitly specify to what
    # tab it should redirect after action, until the coflict will
    # be fixed in Horizon.
    def get_index_url(self):
        """This url is used both as success and failure url"""
        return "%s?tab=resource_management_tabs__resource_classes_tab" %\
            reverse("horizon:infrastructure:resource_management:index")

    def get_success_url(self):
        return self.get_index_url()

    def get_failure_url(self):
        return self.get_index_url()

    def format_status_message(self, message):
        name = self.context.get('name')
        return message % name

    def _get_flavors(self, request, data):
        flavors = []
        flavor_ids = data.get('flavors_object_ids') or []
        max_vms = data.get('max_vms')
        resource_class_name = data['name']
        for template_id in flavor_ids:
            template = api.tuskar.FlavorTemplate.get(request, template_id)
            capacities = []
            for c in template.capacities:
                capacities.append({'name': c.name,
                                   'value': str(c.value),
                                   'unit': c.unit})
            # FIXME: tuskar uses resource-class-name prefix for flavors,
            # e.g. m1.large, we add rc name to the template name:
            flavor_name = "%s.%s" % (resource_class_name, template.name)
            flavors.append({'name': flavor_name,
                            'max_vms': max_vms.get(template.id, None),
                            'capacities': capacities})
        return flavors

    def _add_racks(self, request, data, resource_class):
        ids_to_add = data.get('racks_object_ids') or []
        resource_class.set_racks(request, ids_to_add)


class CreateResourceClass(ResourceClassWorkflowMixin, workflows.Workflow):
    default_steps = (CreateResourceClassInfoAndFlavors,
                     CreateRacks)

    slug = "create_resource_class"
    name = _("Create Class")
    finalize_button_name = _("Create Class")
    success_message = _('Created class "%s".')
    failure_message = _('Unable to create  class "%s".')

    def _create_resource_class_info(self, request, data):
        try:
            flavors = self._get_flavors(request, data)
            return api.tuskar.ResourceClass.create(
                request,
                name=data['name'],
                service_type=data['service_type'],
                flavors=flavors)
        except:
            redirect = self.get_failure_url()
            exceptions.handle(request,
                              _('Unable to create resource class.'),
                              redirect=redirect)
            return None

    def handle(self, request, data):
        resource_class = self._create_resource_class_info(request, data)
        self._add_racks(request, data, resource_class)
        return True


class UpdateResourceClassInfoAndFlavors(CreateResourceClassInfoAndFlavors):
    depends_on = ("resource_class_id",)


class UpdateRacks(CreateRacks):
    depends_on = ("resource_class_id",)


class UpdateResourceClass(ResourceClassWorkflowMixin, workflows.Workflow):
    default_steps = (UpdateResourceClassInfoAndFlavors,
                     UpdateRacks)

    slug = "update_resource_class"
    name = _("Update Class")
    finalize_button_name = _("Update Class")
    success_message = _('Updated class "%s".')
    failure_message = _('Unable to update class "%s".')

    def _update_resource_class_info(self, request, data):
        try:
            flavors = self._get_flavors(request, data)
            return api.tuskar.ResourceClass.update(
                    request,
                    data['resource_class_id'],
                    name=data['name'],
                    service_type=data['service_type'],
                    flavors=flavors)
        except:
            redirect = self.get_failure_url()
            exceptions.handle(request,
                              _('Unable to create resource class.'),
                              redirect=redirect)
            return None

    def handle(self, request, data):
        resource_class = self._update_resource_class_info(request, data)
        self._add_racks(request, data, resource_class)
        return True


class DetailUpdateWorkflow(UpdateResourceClass):
    def get_index_url(self):
        """This url is used both as success and failure url"""
        url = "horizon:infrastructure:resource_management:resource_classes:"\
              "detail"
        return "%s?tab=resource_class_details__overview" % (
            reverse(url, args=(self.context["resource_class_id"])))


class UpdateRacksWorkflow(UpdateResourceClass):
    def get_index_url(self):
        """This url is used both as success and failure url"""
        url = "horizon:infrastructure:resource_management:resource_classes:"\
              "detail"
        return "%s?tab=resource_class_details__racks" % (
            reverse(url, args=(self.context["resource_class_id"])))


class UpdateFlavorsWorkflow(UpdateResourceClass):
    def get_index_url(self):
        """This url is used both as success and failure url"""
        url = "horizon:infrastructure:resource_management:resource_classes:"\
              "detail"
        return "%s?tab=resource_class_details__flavors" % (
            reverse(url, args=(self.context["resource_class_id"])))
