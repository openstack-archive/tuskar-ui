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
from horizon import tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure. \
    resource_management.flavor_templates.tables import FlavorTemplatesTable
from tuskar_ui.infrastructure. \
    resource_management.racks.tables import RacksTable
from tuskar_ui.infrastructure. \
    resource_management.resource_classes.tables import ResourceClassesTable


class RacksTab(tabs.TableTab):
    table_classes = (RacksTable,)
    name = _("Racks")
    slug = "racks_tab"
    template_name = ("infrastructure/resource_management/"
                    "racks/_index_table.html")

    def get_racks_data(self):
        try:
            racks = tuskar.Rack.list(self.request)
        except:
            racks = []
            exceptions.handle(self.request,
                              _('Unable to retrieve racks.'))
        return racks

    def get_context_data(self, request):
        context = super(RacksTab, self).get_context_data(request)
        try:
            context["nodes"] = tuskar.Node.list_unracked(self.request)
        except:
            context["nodes"] = []
            exceptions.handle(request,
                              _('Unable to retrieve nodes.'))
        return context


class FlavorTemplatesTab(tabs.TableTab):
    table_classes = (FlavorTemplatesTable,)
    name = _("Flavor Templates")
    slug = "flavor_templates_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_flavor_templates_data(self):
        try:
            flavor_templates = tuskar.FlavorTemplate.list(self.request)
        except:
            flavor_templates = []
            exceptions.handle(self.request,
                              _('Unable to retrieve Tuskar Flavor Templates.'))
        return flavor_templates


class ResourceClassesTab(tabs.TableTab):
    table_classes = (ResourceClassesTable,)
    name = _("Classes")
    slug = "resource_classes_tab"
    template_name = "horizon/common/_detail_table.html"
    #preload = False buggy, checkboxes doesn't work wit table actions

    def get_resource_classes_data(self):
        try:
            resource_classes = tuskar.ResourceClass.list(self.request)
        except:
            resource_classes = []
            exceptions.handle(self.request,
                              _('Unable to retrieve resource classes list.'))
        return resource_classes


class ResourceManagementTabs(tabs.TabGroup):
    slug = "resource_management_tabs"
    tabs = (ResourceClassesTab, RacksTab, FlavorTemplatesTab)
    sticky = True
