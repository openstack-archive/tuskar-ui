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
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui import utils


def _get_role_data(overcloud, role):
    resources = overcloud.resources(role, with_joins=True)
    nodes = [r.node for r in resources]
    node_count = len(nodes)
    data = {
        'role': role,
        'name': role.name,
        'node_count': node_count,
    }
    if nodes:
        running_node_count = sum(1 for node in nodes
                                 if node.instance.status == 'ACTIVE')
        error_node_count = sum(1 for node in nodes
                               if node.instance.status == 'ERROR')
        deploying_node_count = (node_count - error_node_count -
                                running_node_count)
        data.update({
            'running_node_count': running_node_count,
            'error_node_count': error_node_count,
            'error_node_message': ungettext_lazy("node is down",
                                                 "nodes are down",
                                                 error_node_count),
            'deploying_node_count': deploying_node_count,
            'deploying_node_message': ungettext_lazy("node is deploying",
                                                     "nodes are deploying",
                                                     deploying_node_count),
        })
        # TODO(rdopieralski) get this from ceilometer
        # data['capacity'] = 20
    return data


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "infrastructure/overcloud/_detail_overview.html"
    preload = False

    def get_context_data(self, request, **kwargs):
        overcloud = self.tab_group.kwargs['overcloud']
        roles = api.OvercloudRole.list(request)
        role_data = [_get_role_data(overcloud, role) for role in roles]
        total = sum(d['node_count'] for d in role_data)
        progress = 100 * sum(d.get('running_node_count', 0)
                             for d in role_data) // (total or 1)

        events = overcloud.stack_events
        last_failed_events = [e for e in events
                              if e.resource_status == 'CREATE_FAILED'][-3:]
        return {
            'overcloud': overcloud,
            'roles': role_data,
            'progress': progress,
            'dashboard_urls': overcloud.dashboard_urls,
            'last_failed_events': last_failed_events,
        }


class ConfigurationTab(tabs.TableTab):
    table_classes = (tables.ConfigurationTable,)
    name = _("Configuration")
    slug = "configuration"
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def get_configuration_data(self):
        overcloud = self.tab_group.kwargs['overcloud']

        return [(utils.de_camel_case(key), value) for key, value in
                overcloud.stack.parameters.items()]


class LogTab(tabs.TableTab):
    table_classes = (tables.LogTable,)
    name = _("Log")
    slug = "log"
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def get_log_data(self):
        overcloud = self.tab_group.kwargs['overcloud']
        return overcloud.stack_events


class DetailTabs(tabs.TabGroup):
    slug = "detail"
    tabs = (OverviewTab, ConfigurationTab, LogTab)
    sticky = True
