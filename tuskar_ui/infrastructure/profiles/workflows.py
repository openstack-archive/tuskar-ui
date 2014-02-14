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

from django.utils.translation import ugettext_lazy as _

from horizon import workflows

from openstack_dashboard.dashboards.admin.flavors \
    import workflows as flavor_workflows


_PROFILE_ID_HELP_TEXT = _("Node profile ID should be UUID4 or integer. "
                          "Leave this field blank or use 'auto' to set "
                          "a random UUID4.")


def _convert_fields_from_flavor(fields):
    # Delete what is not applicable to hardware
    del fields['eph_gb']
    del fields['swap_mb']
    # Alter user-visible strings
    fields['vcpus'].label = _("CPUs")
    fields['disk_gb'].label = _("Disk GB")
    fields['flavor_id'].help_text = _PROFILE_ID_HELP_TEXT


class CreateProfileAction(flavor_workflows.CreateFlavorInfoAction):

    def __init__(self, *args, **kwrds):
        super(CreateProfileAction, self).__init__(*args, **kwrds)
        _convert_fields_from_flavor(self.fields)

    class Meta:
        name = _("Node Profile")
        # FIXME(dtantsur): maybe better help text?
        help_text = _("From here you can create a new "
                      "node profile to organize instance resources.")


class UpdateProfileAction(flavor_workflows.UpdateFlavorInfoAction):

    def __init__(self, *args, **kwargs):
        super(UpdateProfileAction, self).__init__(*args, **kwargs)
        _convert_fields_from_flavor(self.fields)

    class Meta:
        name = _("Node Profile")
        slug = 'update_profile'
        help_text = _("From here you can edit the node profile details.")


class CreateProfileStep(workflows.Step):
    action_class = CreateProfileAction
    contributes = ("flavor_id",
                   "name",
                   "vcpus",
                   "memory_mb",
                   "disk_gb")


class UpdateProfileStep(workflows.Step):
    action_class = UpdateProfileAction
    depends_on = ("flavor_id",)
    contributes = ("name",
                   "vcpus",
                   "memory_mb",
                   "disk_gb")


def _update_arch(request, data):
    # TODO(dtantsur)
    return True


class CreateProfile(flavor_workflows.CreateFlavor):
    slug = "create_profile"
    name = _("Create Node Profile")
    finalize_button_name = _("Create Node Profile")
    success_message = _('Created new node profile "%s".')
    failure_message = _('Unable to create node profile "%s".')
    success_url = "horizon:infrastructure:profiles:index"
    default_steps = (CreateProfileStep,)

    def handle(self, request, data):
        data = dict(data, flavor_access=(), eph_gb=0, swap_mb=0)
        return super(CreateProfile, self).handle(request, data) \
            and _update_arch(request, data)


class UpdateProfile(flavor_workflows.UpdateFlavor):
    slug = "update_profile"
    name = _("Edit Node Profile")
    finalize_button_name = _("Save")
    success_message = _('Modified node profile "%s".')
    failure_message = _('Unable to modify node profile "%s".')
    success_url = "horizon:infrastructure:profiles:index"
    default_steps = (UpdateProfileStep,)

    def handle(self, request, data):
        data = dict(data, flavor_access=(), eph_gb=0, swap_mb=0)
        return super(UpdateProfile, self).handle(request, data) \
            and _update_arch(request, data)
