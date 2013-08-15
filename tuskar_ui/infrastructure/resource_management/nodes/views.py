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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management.nodes.tables \
    import UnrackedNodesTable
from tuskar_ui.infrastructure.resource_management.nodes.tabs \
    import NodeDetailTabs


class UnrackedView(tables.DataTableView):
    table_class = UnrackedNodesTable
    template_name = 'infrastructure/resource_management/nodes/unracked.html'

    def get_data(self):
        try:
            nodes = tuskar.Node.list_unracked(self.request)
        except Exception:
            nodes = []
            exceptions.handle(self.request,
                              _('Unable to retrieve nodes.'))
        return nodes


class DetailView(tabs.TabView):
    tab_group_class = NodeDetailTabs
    template_name = 'infrastructure/resource_management/nodes/detail.html'

    def get_context_data(self, **kwargs):
            context = super(DetailView, self).get_context_data(**kwargs)
            context["node"] = self.get_data()
            return context

    def get_data(self):
        if not hasattr(self, "_node"):
            try:
                node_id = self.kwargs['node_id']
                node = tuskar.Node.get(self.request, node_id)
            except Exception:
                redirect = reverse('horizon:infrastructure:'
                                   'resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'node "%s".')
                                    % node_id,
                                    redirect=redirect)
            self._node = node
        return self._node

    def get_tabs(self, request, *args, **kwargs):
        node = self.get_data()
        return self.tab_group_class(request, node=node,
                                    **kwargs)
