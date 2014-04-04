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

import heatclient
from horizon import tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui import utils


def _get_role_data(overcloud, role):
    """Gathers data about a single deployment role from the related Overcloud
    and OvercloudRole objects, and presents it in the form convenient for use
    from the template.

    :param overcloud: Overcloud object
    :type  overcloud: tuskar_ui.api.Overcloud
    :param role: Role object
    :type  role: tuskar_ui.api.OvercloudRole
    :return: dict with information about the role, to be used by template
    :rtype:  dict
    """
    resources = overcloud.resources(role, with_joins=True)
    nodes = [r.node for r in resources]
    counts = getattr(overcloud, 'counts', [])

    for c in counts:
        if c['overcloud_role_id'] == role.id:
            node_count = c['num_nodes']
            break
    else:
        node_count = 0

    data = {
        'role': role,
        'name': role.name,
        'total_node_count': node_count,
    }
    deployed_node_count = 0
    deploying_node_count = 0
    error_node_count = 0
    waiting_node_count = node_count

    if nodes:
        deployed_node_count = sum(1 for node in nodes
                                  if node.instance.status == 'ACTIVE')
        deploying_node_count = sum(1 for node in nodes
                                   if node.instance.status == 'BUILD')
        error_node_count = sum(1 for node in nodes
                               if node.instance.status == 'ERROR')
        waiting_node_count = (node_count - deployed_node_count -
                              deploying_node_count - error_node_count)

    data.update({
        'deployed_node_count': deployed_node_count,
        'deploying_node_count': deploying_node_count,
        'waiting_node_count': waiting_node_count,
        'error_node_count': error_node_count,
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
        total = sum(d['total_node_count'] for d in role_data)
        progress = 100 * sum(d.get('deployed_node_count', 0)
                             for d in role_data) // (total or 1)

        events = overcloud.stack_events
        last_failed_events = [e for e in events
                              if e.resource_status == 'CREATE_FAILED'][-3:]
        return {
            'overcloud': overcloud,
            'roles': role_data,
            'progress': max(5, progress),
            'dashboard_urls': overcloud.dashboard_urls,
            'last_failed_events': last_failed_events,
        }


class UndeployInProgressTab(tabs.Tab):
    name = _("Overview")
    slug = "undeploy_in_progress_tab"
    template_name = "infrastructure/overcloud/_undeploy_in_progress.html"
    preload = False

    def get_context_data(self, request, **kwargs):
        overcloud = self.tab_group.kwargs['overcloud']

        # TODO(lsmola) since at this point we don't have total number of nodes
        # we will hack this around, till API can show this information. So it
        # will actually show progress like the total number is 10, or it will
        # show progress of 5%. Ugly, but workable.
        total_num_nodes_count = 10

        try:
            all_resources_count = len(
                overcloud.all_resources(with_joins=False))
        except heatclient.exc.HTTPNotFound:
            # Immediately after undeploying has started, heat returns this
            # exception so we can take it as kind of init of undeploying.
            all_resources_count = total_num_nodes_count

        # TODO(lsmola) same as hack above
        total_num_nodes_count = max(all_resources_count, total_num_nodes_count)

        delete_progress = max(
            5, 100 * (total_num_nodes_count - all_resources_count))

        events = overcloud.stack_events
        last_failed_events = [e for e in events
                              if e.resource_status == 'DELETE_FAILED'][-3:]
        return {
            'overcloud': overcloud,
            'progress': delete_progress,
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


class UndeployInProgressTabs(tabs.TabGroup):
    slug = "undeploy_in_progress"
    tabs = (UndeployInProgressTab, LogTab)
    sticky = True


class DetailTabs(tabs.TabGroup):
    slug = "detail"
    tabs = (OverviewTab, ConfigurationTab, LogTab)
    sticky = True
