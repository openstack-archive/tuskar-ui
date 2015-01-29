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
from openstack_dashboard.api import glance
from openstack_dashboard.dashboards.admin.flavors import (
    workflows as flavor_workflows)

from tuskar_ui import api
from tuskar_ui.utils import utils


class CreateFlavorAction(flavor_workflows.CreateFlavorInfoAction):
    arch = fields.ChoiceField(choices=(('i386', 'i386'), ('amd64', 'amd64'),
                                       ('x86_64', 'x86_64')),
                              label=_("Architecture"))
    kernel_image_id = fields.ChoiceField(choices=(),
                                         label=_("Deploy Kernel Image"))
    ramdisk_image_id = fields.ChoiceField(choices=(),
                                          label=_("Deploy Ramdisk Image"))

    def __init__(self, *args, **kwrds):
        super(CreateFlavorAction, self).__init__(*args, **kwrds)
        try:
            kernel_images = glance.image_list_detailed(
                self.request,
            )[0]
            kernel_images = [image for image in kernel_images
                             if utils.check_image_type(image,
                                                       'discovery kernel')]
            ramdisk_images = glance.image_list_detailed(
                self.request,
            )[0]
            ramdisk_images = [image for image in ramdisk_images
                              if utils.check_image_type(image,
                                                        'discovery ramdisk')]
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve images list.'))
            kernel_images = []
            ramdisk_images = []
        self.fields['kernel_image_id'].choices = [(img.id, img.name)
                                                  for img in kernel_images]
        self.fields['ramdisk_image_id'].choices = [(img.id, img.name)
                                                   for img in ramdisk_images]
        # Delete what is not applicable to hardware
        del self.fields['eph_gb']
        del self.fields['swap_mb']
        # Alter user-visible strings
        self.fields['vcpus'].label = _("CPUs")
        self.fields['disk_gb'].label = _("Disk GB")
        # No idea why Horizon exposes this database detail
        del self.fields['flavor_id']

    class Meta:
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
                   "arch",
                   "kernel_image_id",
                   "ramdisk_image_id")


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
                cpu_arch=data['arch'],
                kernel_image_id=data['kernel_image_id'],
                ramdisk_image_id=data['ramdisk_image_id']
            )
        except Exception:
            exceptions.handle(request, _("Unable to create flavor"))
            return False
        return True
