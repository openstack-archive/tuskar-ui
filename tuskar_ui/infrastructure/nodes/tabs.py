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

import itertools

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tabs
from horizon.utils import functions
from openstack_dashboard.api import base as api_base

from tuskar_ui import api
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.infrastructure.nodes import tables
from tuskar_ui.utils import metering as metering_utils
from tuskar_ui.utils import utils


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "infrastructure/nodes/_overview.html"

    def get_context_data(self, request):
        nodes = api.node.Node.list(request)
        cpus = sum(int(node.cpus) for node in nodes if node.cpus)
        memory_mb = sum(int(node.memory_mb) for node in nodes if
                        node.memory_mb)
        local_gb = sum(int(node.local_gb) for node in nodes if node.local_gb)

        nodes_provisioned = api.node.Node.list(request, associated=True)
        nodes_free = api.node.Node.list(request, associated=False)
        nodes_all_count = (utils.length(nodes_provisioned) +
                           utils.length(nodes_free))

        nodes_provisioned_maintenance = list(utils.filter_items(
            nodes_provisioned, maintenance__in=[True]))
        nodes_provisioned = list(
            set(nodes_provisioned) - set(nodes_provisioned_maintenance))

        nodes_free_maintenance = list(utils.filter_items(
            nodes_free, maintenance__in=[True]))
        nodes_free = list(
            set(nodes_free) - set(nodes_free_maintenance))

        nodes_maintenance = (
            nodes_provisioned_maintenance + nodes_free_maintenance)

        nodes_provisioned_down = utils.filter_items(
            nodes_provisioned, power_state__not_in=api.node.POWER_ON_STATES)
        nodes_free_down = utils.filter_items(
            nodes_free, power_state__not_in=api.node.POWER_ON_STATES)

        nodes_down = itertools.chain(nodes_provisioned_down, nodes_free_down)
        nodes_up = utils.filter_items(
            nodes, power_state__in=api.node.POWER_ON_STATES)

        context = {
            'cpus': cpus,
            'memory_gb': memory_mb / 1024.0,
            'local_gb': local_gb,
            'nodes_up_count': utils.length(nodes_up),
            'nodes_down_count': utils.length(nodes_down),
            'nodes_provisioned_count': utils.length(nodes_provisioned),
            'nodes_free_count': utils.length(nodes_free),
            'nodes_maintenance_count': utils.length(nodes_maintenance),
            'nodes_all_count': nodes_all_count
        }

        if api_base.is_service_enabled(self.request, 'metering'):
            context['meter_conf'] = (
                (_('System Load'),
                 metering_utils.url_part('hardware.cpu.load.1min', False),
                 None),
                (_('CPU Utilization'),
                 metering_utils.url_part('hardware.system_stats.cpu.util',
                                         True),
                 '100'),
                (_('Swap Utilization'),
                 metering_utils.url_part('hardware.memory.swap.util',
                                         True),
                 '100'),
            )

        return context


class RegisteredTab(tabs.TableTab):
    table_classes = (tables.RegisteredNodesTable,)
    name = _("Registered")
    slug = "registered"
    template_name = "horizon/common/_detail_table.html"

    def __init__(self, tab_group, request):
        super(RegisteredTab, self).__init__(tab_group, request)

    def get_items_count(self):
        return len(self._nodes)

    @cached_property
    def _nodes(self):
        redirect = urlresolvers.reverse('horizon:infrastructure:nodes:index')

        if 'provisioned' in self.request.GET:
            associated = True
        elif 'free' in self.request.GET:
            associated = False
        else:
            associated = None

        return api.node.Node.list(self.request, associated=associated,
                                  maintenance=False, _error_redirect=redirect)

    @cached_property
    def _nodes_info(self):
        page_size = functions.get_page_size(self.request)

        prev_marker = self.request.GET.get(
            tables.RegisteredNodesTable._meta.prev_pagination_param, None)

        if prev_marker is not None:
            sort_dir = 'asc'
            marker = prev_marker
        else:
            sort_dir = 'desc'
            marker = self.request.GET.get(
                tables.RegisteredNodesTable._meta.pagination_param, None)

        nodes = self._nodes

        if marker:
            node_ids = [node.uuid for node in self._nodes]
            position = node_ids.index(marker)
            if sort_dir == 'asc':
                start = max(0, position - page_size)
                end = position
            else:
                start = position + 1
                end = start + page_size
        else:
            start = 0
            end = page_size

        prev = start != 0
        more = len(nodes) > end
        return nodes[start:end], prev, more

    def get_nodes_table_data(self):
        nodes, prev, more = self._nodes_info

        if 'errors' in self.request.GET:
            return api.node.filter_nodes(nodes, healthy=False)

        if nodes:
            all_resources = api.heat.Resource.list_all_resources(self.request)
            for node in nodes:
                try:
                    resource = api.heat.Resource.get_by_node(
                        self.request, node, all_resources=all_resources)
                    node.role_name = resource.role.name
                    node.role_id = resource.role.id
                    node.stack_id = resource.stack.id
                except exceptions.NotFound:
                    node.role_name = '-'

        return nodes

    def has_prev_data(self, table):
        return self._nodes_info[1]

    def has_more_data(self, table):
        return self._nodes_info[2]


class MaintenanceTab(tabs.TableTab):
    table_classes = (tables.MaintenanceNodesTable,)
    name = _("Maintenance")
    slug = "maintenance"
    template_name = "horizon/common/_detail_table.html"

    def get_items_count(self):
        return len(self.get_maintenance_nodes_table_data())

    def get_maintenance_nodes_table_data(self):
        redirect = urlresolvers.reverse('horizon:infrastructure:nodes:index')
        nodes = api.node.Node.list(self.request, maintenance=True,
                                   _error_redirect=redirect)
        return nodes


class DetailOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "detail_overview"
    template_name = 'infrastructure/nodes/_detail_overview.html'

    def get_context_data(self, request):
        node = self.tab_group.kwargs['node']
        context = {'node': node}
        try:
            resource = api.heat.Resource.get_by_node(self.request, node)
            context['role'] = resource.role
            context['stack'] = resource.stack
        except exceptions.NotFound:
            pass
        if node.instance_uuid:
            if api_base.is_service_enabled(self.request, 'metering'):
                # Meter configuration in the following format:
                # (meter label, url part, barchart (True/False))
                context['meter_conf'] = (
                    (_('System Load'),
                     metering_utils.url_part('hardware.cpu.load.1min', False),
                     None),
                    (_('CPU Utilization'),
                     metering_utils.url_part('hardware.system_stats.cpu.util',
                                             True),
                     '100'),
                    (_('Swap Utilization'),
                     metering_utils.url_part('hardware.memory.swap.util',
                                             True),
                     '100'),
                    (_('Disk I/O '),
                     metering_utils.url_part('disk-io', False),
                     None),
                    (_('Network I/O '),
                     metering_utils.url_part('network-io', False),
                     None),
                )
        return context


class NodeTabs(tabs.TabGroup):
    slug = "nodes"
    tabs = (OverviewTab, RegisteredTab)
    sticky = True
    template_name = "horizon/common/_items_count_tab_group.html"

    def __init__(self, request, **kwargs):
        if api.node.NodeClient.ironic_enabled(request):
            self.tabs = self.tabs + (MaintenanceTab,)
        super(NodeTabs, self).__init__(request, **kwargs)


class NodeDetailTabs(tabs.TabGroup):
    slug = "node_details"
    tabs = (DetailOverviewTab,)
