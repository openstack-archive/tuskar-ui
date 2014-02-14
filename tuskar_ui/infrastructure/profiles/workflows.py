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

from django.forms import fields
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.flavors \
    import workflows as flavor_workflows


def _convert_fields_from_flavor(fields):
    # Delete what is not applicable to hardware
    del fields['eph_gb']
    del fields['swap_mb']
    # No idea why Horizon exposes this database detail
    del fields['flavor_id']
    # Alter user-visible strings
    fields['vcpus'].label = _("CPUs")
    fields['disk_gb'].label = _("Disk GB")


class CreateProfileAction(flavor_workflows.CreateFlavorInfoAction):
    arch = fields.ChoiceField(choices=(('i386', 'i386'), ('amd64', 'amd64')),
                              label=_("Architecture"))

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
    contributes = ("name",
                   "vcpus",
                   "memory_mb",
                   "disk_gb",
                   "arch")


class UpdateProfileStep(workflows.Step):
    action_class = UpdateProfileAction
    depends_on = ("flavor_id",)
    contributes = ("name",
                   "vcpus",
                   "memory_mb",
                   "disk_gb",
                   "arch")


def _update_arch(request, data, flavor_id=None):
    # FIXME(dtantsur): this code is duplicating what is already done
    # in base flavor code when editing. This is because UpdateFlavor.handle
    # has no way of altering extras_dict.
    if flavor_id is None:
        flavor_id = data['flavor_id']
    try:
        extras_dict = api.nova.flavor_get_extras(request, flavor_id, raw=True)
        extras_dict['cpu_arch'] = data.pop('arch')
        api.nova.flavor_extra_set(request, flavor_id, extras_dict)
    except Exception:
        exceptions.handle(request, ignore=True)
        return False
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
        data = dict(data, flavor_access=(), eph_gb=0, swap_mb=0,
                    flavor_id='auto')
        return super(CreateProfile, self).handle(request, data) \
            and _update_arch(request, data, flavor_id=self.object.id)


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
