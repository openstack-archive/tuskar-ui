# Vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management.racks\
    import tables as racks_tables
from tuskar_ui.infrastructure.resource_management.resource_classes\
    import tables as resource_classes_tables


def get_provision_racks_and_state(racks):
    unprovisioned_racks = [rack for rack in racks
                           if not rack.is_provisioned]
    provisioning_racks = [rack for rack in racks
                          if rack.is_provisioning]
    if provisioning_racks:
        state = 'provisioning'
    elif unprovisioned_racks:
        state = 'unprovisioned'
    else:
        state = 'provisioned'
    return unprovisioned_racks, provisioning_racks, state


class ProvisioningInfoMixin(object):
    def get_provisioning_racks_data(self):
        try:
            racks = tuskar.Rack.list(self.request)
        except Exception:
            racks = []
            exceptions.handle(self.request, _("Unable to retrieve racks."))
        return racks

    def get_context_data(self, request=None, **kwargs):
        # XXX get_context_data has different signatures in different views
        if request:
            context = super(ProvisioningInfoMixin, self).get_context_data(
                request, **kwargs)
        else:
            context = super(ProvisioningInfoMixin, self).get_context_data(
                **kwargs)
        (unprovisioned_racks, provisioning_racks, state) = (
            get_provision_racks_and_state(self.
                                          get_provisioning_racks_data()))
        context.update({
            'unprovisioned_racks': unprovisioned_racks,
            'provisioning_racks': provisioning_racks,
            'provisioning_state': state,
        })
        return context


class RacksTab(ProvisioningInfoMixin, tabs.TableTab):
    table_classes = (racks_tables.RacksTable,)
    name = _("Racks")
    slug = "racks_tab"
    template_name = ("infrastructure/resource_management/"
                     "racks/_index_table.html")

    def get_racks_data(self):
        try:
            racks = tuskar.Rack.list(self.request)
        except Exception:
            racks = []
            exceptions.handle(self.request,
                              _('Unable to retrieve racks.'))
        return racks

    def get_context_data(self, request):
        context = super(RacksTab, self).get_context_data(request)
        try:
            context["baremetal_nodes"] = tuskar.BaremetalNode.list_unracked(
                self.request)
        except Exception:
            context["baremetal_nodes"] = []
            exceptions.handle(request,
                              _("Unable to retrieve baremetal nodes."))
        return context


class ResourceClassesTab(ProvisioningInfoMixin, tabs.TableTab):
    table_classes = (resource_classes_tables.ResourceClassesTable,)
    name = _("Classes")
    slug = "resource_classes_tab"
    template_name = ("infrastructure/resource_management/"
                     "resource_classes/_index_table.html")
    #preload = False buggy, checkboxes doesn't work wit table actions

    def get_resource_classes_data(self):
        try:
            resource_classes = tuskar.ResourceClass.list(self.request)
        except Exception:
            resource_classes = []
            exceptions.handle(self.request,
                              _('Unable to retrieve resource classes list.'))
        return resource_classes


class ResourceManagementTabs(tabs.TabGroup):
    slug = "resource_management_tabs"
    tabs = (ResourceClassesTab, RacksTab)
    sticky = True
