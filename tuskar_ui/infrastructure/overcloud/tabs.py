# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from horizon import exceptions
from horizon import tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("infrastructure/overcloud/_detail_overview.html")

    def get_context_data(self, request):
        context = {}
        overcloud = self.tab_group.kwargs['overcloud']

        try:
            roles = api.OvercloudRole.list(request)
        except Exception:
            roles = {}
            exceptions.handle(request,
                              _('Unable to retrieve overcloud roles.'))

        context['overcloud'] = overcloud
        context['roles'] = []
        for role in roles:
            context['roles'].append(
                self._get_role_data(overcloud, role))

        # also get expected node counts
        return context

    def _get_role_data(self, overcloud, role):
        resources = overcloud.resources(role, with_joins=True)
        nodes = [r.node for r in resources]

        role.node_count = len(nodes)
        if role.node_count > 0:
            role.running_node_count = len(
                [n for n in nodes if n.instance.status == 'ACTIVE'])
            role.error_node_count = len(
                [n for n in nodes if n.instance.status == 'ERROR'])
            role.other_node_count = role.node_count - \
                (role.running_node_count +
                 role.error_node_count)
            role.running_node_percentage = 100 * \
                role.running_node_count / role.node_count
        return role


class ConfigurationTab(tabs.Tab):
    name = _("Configuration")
    slug = "configuration"
    template_name = ("infrastructure/overcloud/_detail_configuration.html")

    def get_context_data(self, request):
        return {}


class LogTab(tabs.TableTab):
    table_classes = (tables.LogTable,)
    name = _("Log")
    slug = "log"
    template_name = "horizon/common/_detail_table.html"

    def get_log_data(self):
        overcloud = self.tab_group.kwargs['overcloud']
        return overcloud.stack_events


class DetailTabs(tabs.TabGroup):
    slug = "detail"
    tabs = (OverviewTab, ConfigurationTab, LogTab)
    sticky = True
