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
from openstack_dashboard.dashboards.admin.flavors import (
    workflows as flavor_workflows)

from tuskar_ui import api


class CreateFlavorAction(flavor_workflows.CreateFlavorInfoAction):
    arch = fields.ChoiceField(choices=(('i386', 'i386'), ('amd64', 'amd64'),
                                       ('x86_64', 'x86_64')),
                              label=_("Architecture"))

    def __init__(self, *args, **kwrds):
        super(CreateFlavorAction, self).__init__(*args, **kwrds)
        # Delete what is not applicable to hardware
        del self.fields['eph_gb']
        del self.fields['swap_mb']
        # Alter user-visible strings
        self.fields['vcpus'].label = _("CPUs")
        self.fields['disk_gb'].label = _("Disk GB")
        # No idea why Horizon exposes this database detail
        del self.fields['flavor_id']

    class Meta(object):
        name = _("Flavor")
        help_text = _("Flavors define the sizes for RAM, disk, number of "
                      "cores, and other resources. Flavors should be "
                      "associated with roles when planning a deployment.")


class CreateFlavorStep(workflows.Step):
    action_class = CreateFlavorAction
    contributes = ("name",
                   "vcpus",
                   "memory_mb",
                   "disk_gb",
                   "arch")


class CreateFlavor(flavor_workflows.CreateFlavor):
    slug = "create_flavor"
    name = _("Create Flavor")
    finalize_button_name = _("Create Flavor")
    success_message = _('Created new flavor "%s".')
    failure_message = _('Unable to create flavor "%s".')
    success_url = "horizon:infrastructure:flavors:index"
    default_steps = (CreateFlavorStep,)

    def handle(self, request, data):
        try:
            self.object = api.flavor.Flavor.create(
                request,
                name=data['name'],
                memory=data['memory_mb'],
                vcpus=data['vcpus'],
                disk=data['disk_gb'],
                cpu_arch=data['arch']
            )
        except Exception:
            exceptions.handle(request, _("Unable to create flavor"))
            return False
        return True
