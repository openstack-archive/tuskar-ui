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
from horizon import tabs
from horizon.utils import functions
from openstack_dashboard.api import base as api_base

from tuskar_ui import api
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.infrastructure.nodes import tables
from tuskar_ui.utils import metering as metering_utils
from tuskar_ui.utils import utils


def filter_extra(nodes, index, value):
    return (node for node in nodes
            if node.extra.get(index, None) == value)


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "infrastructure/nodes/_overview.html"

    def get_context_data(self, request):
        nodes = self.tab_group.kwargs['nodes']
        cpus = sum(int(node.cpus) for node in nodes if node.cpus)
        memory_mb = sum(int(node.memory_mb) for node in nodes if
                        node.memory_mb)
        local_gb = sum(int(node.local_gb) for node in nodes if node.local_gb)

        nodes_provisioned = set(utils.filter_items(
            nodes, provision_state__in=api.node.PROVISION_STATE_PROVISIONED))
        nodes_free = set(utils.filter_items(
            nodes, provision_state__in=api.node.PROVISION_STATE_FREE))
        nodes_deleting = set(utils.filter_items(
            nodes, provision_state__in=api.node.PROVISION_STATE_DELETING))
        nodes_error = set(utils.filter_items(
            nodes, provision_state__in=api.node.PROVISION_STATE_ERROR))

        nodes_provisioned_maintenance = set(utils.filter_items(
            nodes_provisioned, maintenance=True))
        nodes_provisioned_not_maintenance = (
            nodes_provisioned - nodes_provisioned_maintenance)

        nodes_provisioning = set(utils.filter_items(
            nodes,
            provision_state__in=api.node.PROVISION_STATE_PROVISIONING))

        nodes_free_maintenance = set(utils.filter_items(
            nodes_free, maintenance=True))
        nodes_free_not_maintenance = (
            nodes_free - nodes_free_maintenance)

        nodes_maintenance = (
            nodes_provisioned_maintenance | nodes_free_maintenance)

        nodes_provisioned_down = utils.filter_items(
            nodes_provisioned, power_state__not_in=api.node.POWER_ON_STATES)
        nodes_free_down = utils.filter_items(
            nodes_free, power_state__not_in=api.node.POWER_ON_STATES)

        nodes_on_discovery = filter_extra(
            nodes_maintenance, 'on_discovery', 'true')
        nodes_discovered = filter_extra(
            nodes_maintenance, 'newly_discovered', 'true')
        nodes_discovery_failed = filter_extra(
            nodes_maintenance, 'discovery_failed', 'true')

        nodes_down = itertools.chain(nodes_provisioned_down, nodes_free_down)
        nodes_up = utils.filter_items(
            nodes, power_state__in=api.node.POWER_ON_STATES)

        nodes_free_count = len(nodes_free_not_maintenance)
        nodes_provisioned_count = len(
            nodes_provisioned_not_maintenance)
        nodes_provisioning_count = len(nodes_provisioning)
        nodes_maintenance_count = len(nodes_maintenance)
        nodes_deleting_count = len(nodes_deleting)
        nodes_error_count = len(nodes_error)

        context = {
            'cpus': cpus,
            'memory_gb': memory_mb / 1024.0,
            'local_gb': local_gb,
            'nodes_up_count': utils.length(nodes_up),
            'nodes_down_count': utils.length(nodes_down),
            'nodes_provisioned_count': nodes_provisioned_count,
            'nodes_provisioning_count': nodes_provisioning_count,
            'nodes_free_count': nodes_free_count,
            'nodes_deleting_count': nodes_deleting_count,
            'nodes_error_count': nodes_error_count,
            'nodes_maintenance_count': nodes_maintenance_count,
            'nodes_all_count': len(nodes),
            'nodes_on_discovery_count': utils.length(nodes_on_discovery),
            'nodes_discovered_count': utils.length(nodes_discovered),
            'nodes_discovery_failed_count': utils.length(
                nodes_discovery_failed),
            'nodes_status_data':
                'Provisioned={0}|Free={1}|Maintenance={2}'.format(
                    nodes_provisioned_count, nodes_free_count,
                    nodes_maintenance_count)
        }
        # additional node status pie chart data, showing only if it appears
        if nodes_provisioning_count:
            context['nodes_status_data'] += '|Provisioning={0}'.format(
                nodes_provisioning_count)
        if nodes_deleting_count:
            context['nodes_status_data'] += '|Deleting={0}'.format(
                nodes_deleting_count)
        if nodes_error_count:
            context['nodes_status_data'] += '|Error={0}'.format(
                nodes_error_count)

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

        # TODO(akrivoka): Ajaxize these calls so that they don't hold up the
        # whole page load
        context['top_5'] = {
            'fan': metering_utils.get_top_5(request, 'hardware.ipmi.fan'),
            'voltage': metering_utils.get_top_5(
                request, 'hardware.ipmi.voltage'),
            'temperature': metering_utils.get_top_5(
                request, 'hardware.ipmi.temperature'),
            'current': metering_utils.get_top_5(
                request, 'hardware.ipmi.current'),
        }

        return context


class BaseTab(tabs.TableTab):
    table_classes = (tables.BaseNodesTable,)
    name = _("Nodes")
    slug = "nodes"
    template_name = "horizon/common/_detail_table.html"

    def __init__(self, tab_group, request):
        super(BaseTab, self).__init__(tab_group, request)

    @cached_property
    def _nodes(self):
        return []

    def get_items_count(self):
        return len(self._nodes)

    @cached_property
    def _nodes_info(self):
        page_size = functions.get_page_size(self.request)

        prev_marker = self.request.GET.get(
            self.table_classes[0]._meta.prev_pagination_param, None)

        if prev_marker is not None:
            sort_dir = 'asc'
            marker = prev_marker
        else:
            sort_dir = 'desc'
            marker = self.request.GET.get(
                self.table_classes[0]._meta.pagination_param, None)

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

    def get_base_nodes_table_data(self):
        nodes, prev, more = self._nodes_info
        return nodes

    def has_prev_data(self, table):
        return self._nodes_info[1]

    def has_more_data(self, table):
        return self._nodes_info[2]


class AllTab(BaseTab):
    table_classes = (tables.AllNodesTable,)
    name = _("All")
    slug = "all"

    def __init__(self, tab_group, request):
        super(AllTab, self).__init__(tab_group, request)

    @cached_property
    def _nodes(self):
        return self.tab_group.kwargs['nodes']

    def get_all_nodes_table_data(self):
        nodes, prev, more = self._nodes_info
        return nodes


class ProvisionedTab(BaseTab):
    table_classes = (tables.ProvisionedNodesTable,)
    name = _("Provisioned")
    slug = "provisioned"

    def __init__(self, tab_group, request):
        super(ProvisionedTab, self).__init__(tab_group, request)

    @cached_property
    def _nodes(self):
        redirect = urlresolvers.reverse('horizon:infrastructure:nodes:index')
        return api.node.Node.list(self.request, associated=True,
                                  maintenance=False, _error_redirect=redirect)

    def get_provisioned_nodes_table_data(self):
        nodes, prev, more = self._nodes_info

        if nodes:
            for node in nodes:
                try:
                    resource = api.heat.Resource.get_by_node(
                        self.request, node)
                except LookupError:
                    node.role_name = '-'
                else:
                    node.role_name = resource.role.name
                    node.role_id = resource.role.id
                    node.stack_id = resource.stack.id

        return nodes


class FreeTab(BaseTab):
    table_classes = (tables.FreeNodesTable,)
    name = _("Free")
    slug = "free"

    def __init__(self, tab_group, request):
        super(FreeTab, self).__init__(tab_group, request)

    @cached_property
    def _nodes(self):
        redirect = urlresolvers.reverse('horizon:infrastructure:nodes:index')
        return api.node.Node.list(self.request, associated=False,
                                  maintenance=False, _error_redirect=redirect)

    def get_free_nodes_table_data(self):
        nodes, prev, more = self._nodes_info
        return nodes


class MaintenanceTab(BaseTab):
    table_classes = (tables.MaintenanceNodesTable,)
    name = _("Maintenance")
    slug = "maintenance"

    def __init__(self, tab_group, request):
        super(MaintenanceTab, self).__init__(tab_group, request)

    @cached_property
    def _nodes(self):
        nodes = self.tab_group.kwargs['nodes']
        return list(utils.filter_items(nodes, maintenance=True))

    def get_maintenance_nodes_table_data(self):
        return self._nodes


class DetailOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "detail_overview"
    template_name = 'infrastructure/nodes/_detail_overview.html'

    def get_context_data(self, request):
        node = self.tab_group.kwargs['node']
        context = {'node': node}
        try:
            resource = api.heat.Resource.get_by_node(self.request, node)
        except LookupError:
            pass
        else:
            context['role'] = resource.role
            context['stack'] = resource.stack

        kernel_id = node.driver_info.get('deploy_kernel')
        if kernel_id:
            context['kernel_image'] = api.node.image_get(request, kernel_id)

        ramdisk_id = node.driver_info.get('deploy_ramdisk')
        if ramdisk_id:
            context['ramdisk_image'] = api.node.image_get(request, ramdisk_id)

        if node.instance_uuid:
            if api_base.is_service_enabled(self.request, 'metering'):
                # Meter configuration in the following format:
                # (meter label, url part, y_max)
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
                    (_('Current'),
                     metering_utils.url_part('hardware.ipmi.current', False),
                     None),
                    (_('Network IO'),
                     metering_utils.url_part('network-io', False),
                     None),
                    (_('Disk IO'),
                     metering_utils.url_part('disk-io', False),
                     None),
                    (_('Temperature'),
                     metering_utils.url_part('hardware.ipmi.temperature',
                                             False),
                     None),
                    (_('Fan Speed'),
                     metering_utils.url_part('hardware.ipmi.fan', False),
                     None),
                    (_('Voltage'),
                     metering_utils.url_part('hardware.ipmi.voltage', False),
                     None),
                )
        return context


class NodeTabs(tabs.TabGroup):
    slug = "nodes"
    tabs = (OverviewTab, AllTab, ProvisionedTab, FreeTab, MaintenanceTab,)
    sticky = True
    template_name = "horizon/common/_items_count_tab_group.html"


class NodeDetailTabs(tabs.TabGroup):
    slug = "node_details"
    tabs = (DetailOverviewTab,)
