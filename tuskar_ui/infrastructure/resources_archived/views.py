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

from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tables as horizon_tables

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resources_archived import tables


class IndexView(horizon_tables.DataTableView):
    table_class = tables.ArchivedNodesTable
    template_name = 'infrastructure/resources_archived/index.html'

    def get_data(self):
        try:
            archived_nodes = tuskar.BaremetalNode.list(self.request)
        except Exception:
            archived_nodes = []
            exceptions.hanfle(self.request,
                              _('Unable to retrieve archived nodes.'))
        return archived_nodes
