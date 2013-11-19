# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from tuskar_ui.infrastructure.resource_management.nodes import tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "rack_overview_tab"
    template_name = ("infrastructure/resource_management/racks/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"rack": self.tab_group.kwargs['rack']}


class NodesTab(tabs.TableTab):
    table_classes = (tables.NodesTable,)
    name = _("Nodes")
    slug = "nodes"
    template_name = "horizon/common/_detail_table.html"

    def get_nodes_table_data(self):
        try:
            rack = self.tab_group.kwargs['rack']
            baremetal_nodes = rack.list_baremetal_nodes
        except Exception:
            baremetal_nodes = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve node list.'))
        return baremetal_nodes


class RackDetailTabs(tabs.TabGroup):
    slug = "rack_detail_tabs"
    tabs = (OverviewTab, NodesTab)
    sticky = True
