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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tables as horizon_tables

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.nodes.resource import tables


class IndexView(horizon_tables.DataTableView):
    table_class = tables.ResourceNodesTable
    template_name = 'infrastructure/nodes.resource/index.html'

    def get_data(self):
        try:
            resource_nodes = tuskar.Node.list(self.request, associated=True)
        except Exception:
            resource_nodes = []
            redirect = urlresolvers.reverse(
                'horizon:infrastructure:nodes.overview:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve resource nodes.'),
                              redirect=redirect)
        return resource_nodes
