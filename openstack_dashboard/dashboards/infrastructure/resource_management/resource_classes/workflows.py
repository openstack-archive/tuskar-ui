
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
from horizon import workflows
from horizon import forms

from openstack_dashboard import api

import re

from .tables import FlavorsTable, ResourcesTable


# FIXME active tabs coflict
# When on page with tabs, the workflow with more steps is used,
# there is a conflict of active tabs and it always shows the
# first tab after an action. So I explicitly specify to what
# tab it should redirect after action, until the coflict will
# be fixed in Horizon.
def get_index_url():
    return "%s?tab=resource_management_tabs__resource_classes_tab" %\
        reverse("horizon:infrastructure:resource_management:index")


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
                                              ('storage',
                                              ('Storage')),
                                              ],
                                     widget=forms.Select(
                                         attrs={'class': 'switchable'})
                                     )

    def clean(self):
        cleaned_data = super(ResourceClassInfoAndFlavorsAction,
                             self).clean()

        name = cleaned_data.get('name')
        resource_class_id = self.initial.get('resource_class_id', None)
        try:
            resource_classes = api.management.ResourceClass.list(self.request)
        except:
            resource_classes = []
            msg = _('Unable to get resource class list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise
        if resource_classes is not None:
            for resource_class in resource_classes:
                if resource_class.name == name and (
                        resource_class_id is None or
                        resource_class_id != resource_class.id):
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


class CreateResourceClassInfoAndFlavors(workflows.TableStep):
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
                resource_class = api.management.ResourceClass.get(
                    self.workflow.request,
                    resource_class_id)

                # TODO: lsmola ugly interface, rewrite
                self._tables['flavors'].active_multi_select_values = \
                    resource_class.flavors_ids

                all_flavors = resource_class.all_flavors
            else:
                all_flavors = api.management.Flavor.list(self.workflow.request)
        except:
            all_flavors = []
            exceptions.handle(self.workflow.request,
                              _('Unable to retrieve resource flavors list.'))
        return all_flavors


class ResourcesAction(workflows.Action):
    class Meta:
        name = _("Resources")


class CreateResources(workflows.TableStep):
    table_classes = (ResourcesTable,)

    action_class = ResourcesAction
    contributes = ("resources_object_ids")
    template_name = 'infrastructure/resource_management/'\
                    'resource_classes/_resources_step.html'

    def contribute(self, data, context):
        request = self.workflow.request
        context["resources_object_ids"] =\
            request.POST.getlist("resources_object_ids")

        context.update(data)
        return context

    def get_resources_data(self):
        try:
            resource_class_id = self.workflow.context.get("resource_class_id")
            if resource_class_id:
                resource_class = api.management.ResourceClass.get(
                    self.workflow.request,
                    resource_class_id)
                # TODO: lsmola ugly interface, rewrite
                self._tables['resources'].active_multi_select_values = \
                    resource_class.resources_ids
                resources = \
                    resource_class.all_resources
            else:
                resources = \
                    api.management.Rack.list(self.workflow.request, True)
        except:
            resources = []
            exceptions.handle(self.workflow.request,
                              _('Unable to retrieve resources list.'))

        return resources


class ResourceClassWorkflowMixin:
    def get_success_url(self):
        return get_index_url()

    def get_failure_url(self):
        return get_index_url()

    def format_status_message(self, message):
        name = self.context.get('name')
        return message % name

    def _add_flavors(self, request, data, resource_class):
        ids_to_add = data.get('flavors_object_ids') or []
        max_vms = data.get('max_vms')
        resource_class.set_flavors(request, ids_to_add, max_vms)

    def _add_resources(self, request, data, resource_class):
        ids_to_add = data.get('resources_object_ids') or []
        resource_class.set_resources(request, ids_to_add)


class CreateResourceClass(ResourceClassWorkflowMixin, workflows.Workflow):
    default_steps = (CreateResourceClassInfoAndFlavors,
                     CreateResources)

    slug = "create_resource_class"
    name = _("Create Class")
    finalize_button_name = _("Create Class")
    success_message = _('Created class "%s".')
    failure_message = _('Unable to create  class "%s".')

    def _create_resource_class_info(self, request, data):
        try:
            return api.management.ResourceClass.create(
                request,
                name=data['name'],
                service_type=data['service_type'])
        except:
            redirect = get_index_url()
            exceptions.handle(request,
                              _('Unable to create resource class.'),
                              redirect=redirect)
            return None

    def handle(self, request, data):
        resource_class = self._create_resource_class_info(request, data)
        self._add_resources(request, data, resource_class)
        self._add_flavors(request, data, resource_class)
        return True


class UpdateResourceClassInfoAndFlavors(CreateResourceClassInfoAndFlavors):
    depends_on = ("resource_class_id",)


class UpdateResources(CreateResources):
    depends_on = ("resource_class_id",)


class UpdateResourceClass(ResourceClassWorkflowMixin, workflows.Workflow):
    default_steps = (UpdateResourceClassInfoAndFlavors,
                     UpdateResources)

    slug = "update_resource_class"
    name = _("Update Class")
    finalize_button_name = _("Update Class")
    success_message = _('Updated class "%s".')
    failure_message = _('Unable to update class "%s".')

    def _update_resource_class_info(self, request, data):
        try:
            return api.management.ResourceClass.update(
                request,
                data['resource_class_id'],
                name=data['name'],
                service_type=data['service_type'])
        except:
            redirect = get_index_url()
            exceptions.handle(request,
                              _('Unable to create resource class.'),
                              redirect=redirect)
            return None

    def handle(self, request, data):
        resource_class = self._update_resource_class_info(request, data)
        self._add_resources(request, data, resource_class)
        self._add_flavors(request, data, resource_class)
        return True
