# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
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

from horizon import exceptions
from horizon import messages
from horizon import tabs

from openstack_dashboard.api import management

from .flavors.tables import FlavorsTable
from .racks.tables import RacksTable
from .resource_classes.tables import ResourceClassesTable


class RacksTab(tabs.TableTab):
    table_classes = (RacksTable,)
    name = _("Resources")
    slug = "racks_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_racks_data(self):
        try:
            racks = management.Rack.list(self.request)
        except:
            racks = []
            exceptions.handle(self.request,
                              _('Unable to retrieve racks.'))
        return racks


class FlavorsTab(tabs.TableTab):
    table_classes = (FlavorsTable,)
    name = _("Flavors")
    slug = "flavors_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_flavors_data(self):
        try:
            flavors = management.Flavor.list(self.request)
        except:
            flavors = []
            exceptions.handle(self.request,
                              _('Unable to retrieve management flavors.'))
        return flavors


class ResourceClassesTab(tabs.TableTab):
    table_classes = (ResourceClassesTable,)
    name = _("Classes")
    slug = "resource_classes_tab"
    template_name = "horizon/common/_detail_table.html"
    #preload = False buggy, checkboxes doesn't work wit table actions

    def get_resource_classes_data(self):
        try:
            resource_classes = management.ResourceClass.list(self.request)
        except:
            resource_classes = []
            exceptions.handle(self.request,
                              _('Unable to retrieve resource classes list.'))
        return resource_classes


class ResourceManagementTabs(tabs.TabGroup):
    slug = "resource_management_tabs"
    tabs = (RacksTab, ResourceClassesTab, FlavorsTab,)
    sticky = True
