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

from horizon import tables
from horizon import workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.node_profiles \
    import tables as node_profiles_tables
from tuskar_ui.infrastructure.node_profiles \
    import workflows as node_profiles_workflows


class IndexView(tables.DataTableView):
    table_class = node_profiles_tables.NodeProfilesTable
    template_name = 'infrastructure/node_profiles/index.html'

    def get_data(self):
        node_profiles = api.NodeProfile.list(self.request)
        node_profiles.sort(key=lambda np: (np.vcpus, np.ram, np.disk))
        return node_profiles


class CreateView(workflows.WorkflowView):
    workflow_class = node_profiles_workflows.CreateNodeProfile
    template_name = 'infrastructure/node_profiles/create.html'
