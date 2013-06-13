
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

INDEX_URL = "horizon:infrastructure:resource_management:index"


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

    class Meta:
        name = _("Class Settings")
        help_text = _("From here you can fill the class "
                      "settings and add flavors to class.")


class CreateResourceClassInfoAndFlavors(workflows.Step):
    action_class = ResourceClassInfoAndFlavorsAction
    template_name = 'infrastructure/resource_management/resource_classes/'\
                    '_resource_class_info_and_flavors_step.html'
    contributes = ("name", "service_type", "flavors_object_ids",
                   'flavors_object_ids_max_vms')


class ResourcesAction(workflows.Action):

    class Meta:
        name = _("Resources")


class CreateResources(workflows.Step):
    action_class = ResourcesAction
    contributes = ("resources_object_ids")
    template_name = 'infrastructure/resource_management/'\
                    'resource_classes/_resources_step.html'


class ResourceClassWorkflowMixin:
    def get_success_url(self):
        return reverse(INDEX_URL)

    def get_failure_url(self):
        return reverse(INDEX_URL)

    def format_status_message(self, message):
        name = self.context.get('name')
        return message % name

    def _add_flavors(self, request, data, resource_class):
        pass

    def _add_resources(self, request, data, resource_class):
        pass


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
            redirect = reverse(INDEX_URL)
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
            redirect = reverse(INDEX_URL)
            exceptions.handle(request,
                              _('Unable to create resource class.'),
                              redirect=redirect)
            return None

    def handle(self, request, data):
        resource_class = self._update_resource_class_info(request, data)
        self._add_resources(request, data, resource_class)
        self._add_flavors(request, data, resource_class)
        return True
