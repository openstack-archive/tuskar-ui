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


class CreateNodeProfileAction(flavor_workflows.CreateFlavorInfoAction):
    arch = fields.ChoiceField(choices=(('i386', 'i386'), ('amd64', 'amd64')),
                              label=_("Architecture"))
    kernel_id = fields.ChoiceField(choices=(),
                                   label=_("Deploy Kernel Image"))
    ramdisk_id = fields.ChoiceField(choices=(),
                                    label=_("Deploy Ramdisk Image"))

    def __init__(self, *args, **kwrds):
        super(CreateNodeProfileAction, self).__init__(*args, **kwrds)
        try:
            kernel_images = api.glance.image_list_detailed(
                self.request,
                filters={'disk_format': 'aki'}
            )[0]
            ramdisk_images = api.glance.image_list_detailed(
                self.request,
                filters={'disk_format': 'ari'}
            )[0]
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve images list.'))
        self.fields['kernel_id'].choices = [(img.id, img.name)
                                            for img in kernel_images]
        self.fields['ramdisk_id'].choices = [(img.id, img.name)
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
        name = _("Node Profile")
        # FIXME(dtantsur): maybe better help text?
        help_text = _("From here you can create a new "
                      "node profile to organize instance resources.")


class CreateNodeProfileStep(workflows.Step):
    action_class = CreateNodeProfileAction
    contributes = ("name",
                   "vcpus",
                   "memory_mb",
                   "disk_gb",
                   "arch",
                   "kernel_id",
                   "ramdisk_id")


class CreateNodeProfile(flavor_workflows.CreateFlavor):
    slug = "create_node_profile"
    name = _("Create Node Profile")
    finalize_button_name = _("Create Node Profile")
    success_message = _('Created new node profile "%s".')
    failure_message = _('Unable to create node profile "%s".')
    success_url = "horizon:infrastructure:node_profiles:index"
    default_steps = (CreateNodeProfileStep,)

    def handle(self, request, data):
        data = dict(data, flavor_access=(), eph_gb=0, swap_mb=0,
                    flavor_id='auto')
        if not super(CreateNodeProfile, self).handle(request, data):
            return False

        try:
            extras_dict = api.nova.flavor_get_extras(request,
                                                     self.object.id,
                                                     raw=True) or {}
            extras_dict['cpu_arch'] = data['arch']
            extras_dict['baremetal:deploy_kernel_id'] = data['kernel_id']
            extras_dict['baremetal:deploy_ramdisk_id'] = data['ramdisk_id']
            api.nova.flavor_extra_set(request,
                                      self.object.id,
                                      extras_dict)
        except Exception:
            exceptions.handle(request, ignore=True)
            return False
        return True
