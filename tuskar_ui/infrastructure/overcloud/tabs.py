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
            categories = api.ResourceCategory.list(request)
        except Exception:
            categories = {}
            exceptions.handle(request,
                              _('Unable to retrieve resource categories.'))

        context['overcloud'] = overcloud
        context['categories'] = []
        for category in categories:
            context['categories'].append(
                self._get_category_data(overcloud, category))

        # also get expected instance counts
        return context

    def _get_category_data(self, overcloud, category):
        instances = overcloud.instances(category)
        category.instance_count = len(instances)
        if category.instance_count > 0:
            category.running_instance_count = len(
                [i for i in instances if i.status == 'ACTIVE'])
            category.error_instance_count = len(
                [i for i in instances if i.status == 'ERROR'])
            category.other_instance_count = category.instance_count - \
                (category.running_instance_count +
                 category.error_instance_count)
            category.running_instance_percentage = 100 * \
                category.running_instance_count / category.instance_count
        return category


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
