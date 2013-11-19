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

from horizon import messages
from horizon import tabs
import novaclient
import requests


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "node_overview_tab"
    template_name = ("infrastructure/resource_management/nodes/"
                     "_detail_overview.html")
    preload = False

    def get_context_data(self, request):
        baremetal_node = self.tab_group.kwargs['baremetal_node']
        tuskar_node = baremetal_node.tuskar_node
        if tuskar_node:
            try:
                running_instances = len(tuskar_node.running_virtual_machines)
            except (requests.exceptions.ConnectionError,
                    novaclient.exceptions.Unauthorized):
                running_instances = _("Unknown")
                messages.warning(
                    request,
                    _("Can't retrieve the running instances"
                      "from the overcloud."))
        else:
            running_instances = _("None")

        return {
            'baremetal_node': baremetal_node,
            'tuskar_node': tuskar_node,
            'running_instances': running_instances,
        }


class NodeDetailTabs(tabs.TabGroup):
    slug = "node_detail_tabs"
    tabs = (OverviewTab,)
    sticky = True
