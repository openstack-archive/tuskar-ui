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

from django.utils.translation import ugettext_lazy as _
import horizon.tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.flavors import tables
from tuskar_ui.infrastructure.flavors import utils


class FlavorsTab(horizon.tabs.TableTab):
    name = _("Available")
    slug = 'flavors'
    table_classes = (tables.FlavorsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_items_count(self):
        return len(self.get_flavors_data())

    def get_flavors_data(self):
        flavors = api.flavor.Flavor.list(self.request)
        flavors.sort(key=lambda np: (np.vcpus, np.ram, np.disk))
        return flavors


class FlavorSuggestionsTab(horizon.tabs.TableTab):
    name = _("Suggested")
    slug = 'flavor_suggestions'
    table_classes = (tables.FlavorSuggestionsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_items_count(self):
        return len(self.get_flavor_suggestions_data())

    def get_flavor_suggestions_data(self):
        return list(utils.get_flavor_suggestions(self.request))


class FlavorTabs(horizon.tabs.TabGroup):
    slug = 'flavor_tabs'
    tabs = (
        FlavorsTab,
        FlavorSuggestionsTab,
    )
    sticky = True
    template_name = "horizon/common/_items_count_tab_group.html"
