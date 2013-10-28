# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from tuskar_ui.infrastructure.resource_management.resource_classes\
    import tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("infrastructure/resource_management/resource_classes/"
                     "_detail_overview.html")
    # FIXME charts doesnt work if uncommented
    #preload = False

    def get_context_data(self, request):
        return {"resource_class": self.tab_group.kwargs['resource_class']}


class RacksTab(tabs.TableTab):
    table_classes = (tables.RacksTable,)
    name = _("Racks")
    slug = "racks"
    template_name = ("infrastructure/resource_management/resource_classes/"
                     "_detail_racks.html")

    def get_racks_table_data(self):
        try:
            resource_class = self.tab_group.kwargs['resource_class']
            racks = resource_class.list_racks
        except Exception:
            racks = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve rack list.'))
        return racks


class FlavorsTab(tabs.TableTab):
    table_classes = (tables.FlavorsTable,)
    name = _("Flavors")
    slug = "flavors"
    template_name = ("infrastructure/resource_management/resource_classes/"
                     "_detail_flavors.html")

    def get_flavors_table_data(self):
        try:
            resource_class = self.tab_group.kwargs['resource_class']
            flavors = resource_class.list_flavors
        except Exception:
            flavors = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve flavor list.'))
        return flavors

    def allowed(self, request):
        resource_class = self.tab_group.kwargs['resource_class']
        return resource_class.service_type == "compute"


class ResourceClassDetailTabs(tabs.TabGroup):
    slug = "resource_class_details"
    tabs = (OverviewTab, RacksTab, FlavorsTab)
    sticky = True
