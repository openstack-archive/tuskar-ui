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

from horizon import tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "infrastructure/nodes/_overview.html"

    def get_context_data(self, request):
        deployed_nodes = api.node.Node.list(request, associated=True)
        free_nodes = api.node.Node.list(request, associated=False)
        deployed_nodes_error = api.node.filter_nodes(
            deployed_nodes, healthy=False)
        free_nodes_error = api.node.filter_nodes(free_nodes, healthy=False)
        total_nodes = deployed_nodes + free_nodes
        total_nodes_error = deployed_nodes_error + free_nodes_error
        total_nodes_healthy = api.node.filter_nodes(total_nodes, healthy=True)

        return {
            'total_nodes_healthy': total_nodes_healthy,
            'total_nodes_error': total_nodes_error,
            'deployed_nodes': deployed_nodes,
            'deployed_nodes_error': deployed_nodes_error,
            'free_nodes': free_nodes,
            'free_nodes_error': free_nodes_error,
        }


class DeployedTab(tabs.TableTab):
    table_classes = (tables.DeployedNodesTable,)
    name = _("Deployed")
    slug = "deployed"
    template_name = "horizon/common/_detail_table.html"

    def get_items_count(self):
        return len(self.get_deployed_nodes_data())

    def get_deployed_nodes_data(self):
        redirect = urlresolvers.reverse('horizon:infrastructure:nodes:index')
        deployed_nodes = api.node.Node.list(self.request, associated=True,
                                            _error_redirect=redirect)

        if 'errors' in self.request.GET:
            return api.node.filter_nodes(deployed_nodes, healthy=False)

        for node in deployed_nodes:
            resource = api.heat.Resource.get_by_node(self.request, node)
            if resource:
                node.role_name = resource.role.name
                
        return deployed_nodes


class FreeTab(tabs.TableTab):
    table_classes = (tables.FreeNodesTable,)
    name = _("Free")
    slug = "free"
    template_name = "horizon/common/_detail_table.html"

    def get_items_count(self):
        return len(self.get_free_nodes_data())

    def get_free_nodes_data(self):
        redirect = urlresolvers.reverse('horizon:infrastructure:nodes:index')
        free_nodes = api.node.Node.list(self.request, associated=False,
                                        _error_redirect=redirect)

        if 'errors' in self.request.GET:
            return api.node.filter_nodes(free_nodes, healthy=False)

        return free_nodes


class NodeTabs(tabs.TabGroup):
    slug = "nodes"
    tabs = (OverviewTab, DeployedTab, FreeTab)
    sticky = True
    template_name = "horizon/common/_items_count_tab_group.html"
