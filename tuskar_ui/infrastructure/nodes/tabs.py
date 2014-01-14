# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("infrastructure/nodes/_overview.html")

    def get_context_data(self, request):
        try:
            free_nodes = len(api.Node.list(request, associated=False))
        except Exception:
            free_nodes = 0
            exceptions.handle(request,
                              _('Unable to retrieve free nodes.'))
        try:
            resource_nodes = len(api.Node.list(request, associated=True))
        except Exception:
            resource_nodes = 0
            exceptions.handle(request,
                              _('Unable to retrieve resource nodes.'))
        return {
            'nodes_total': free_nodes + resource_nodes,
            'nodes_resources': resource_nodes,
            'nodes_free': free_nodes,
        }


class ResourceTab(tabs.TableTab):
    table_classes = (tables.ResourceNodesTable,)
    name = _("Resource")
    slug = "resource"
    template_name = ("horizon/common/_detail_table.html")

    def get_resource_nodes_data(self):
        try:
            resource_nodes = api.Node.list(self.request, associated=True)
        except Exception:
            resource_nodes = []
            redirect = urlresolvers.reverse(
                'horizon:infrastructure:nodes:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve resource nodes.'),
                              redirect=redirect)
        return resource_nodes


class FreeTab(tabs.TableTab):
    table_classes = (tables.FreeNodesTable,)
    name = _("Free")
    slug = "free"
    template_name = ("horizon/common/_detail_table.html")

    def get_free_nodes_data(self):
        try:
            free_nodes = api.Node.list(self.request, associated=False)
        except Exception:
            free_nodes = []
            redirect = urlresolvers.reverse(
                'horizon:infrastructure:nodes:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve free nodes.'),
                              redirect=redirect)
        return free_nodes


class NodeTabs(tabs.TabGroup):
    slug = "nodes"
    tabs = (OverviewTab, ResourceTab, FreeTab)
    sticky = True
