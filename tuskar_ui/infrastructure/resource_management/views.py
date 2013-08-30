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

"""
Views for Resource Management.
"""


from horizon import tabs as horizon_tabs

from tuskar_ui.infrastructure.resource_management import tabs


class IndexView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.ResourceManagementTabs
    template_name = 'infrastructure/resource_management/index.html'
