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

import collections

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
import horizon.tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.node_profiles import tables


ProfileSuggestion = collections.namedtuple('ProfileSuggestion', [
    'id',
    'cpu_arch',
    'vcpus',
    'ram',
    'disk'
])


class NodeProfiles(horizon.tabs.TableTab):
    name = _("Node Profiles")
    slug = 'node_profiles'
    table_classes = (tables.NodeProfilesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_node_profiles_data(self):
        node_profiles = api.NodeProfile.list(self.request)
        node_profiles.sort(key=lambda np: (np.vcpus, np.ram, np.disk))
        return node_profiles



class ProfileSuggestions(horizon.tabs.TableTab):
    name = _("Profile Suggestions")
    slug = 'profile_suggestions'
    table_classes = (tables.ProfileSuggestionsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_profile_suggestions_data(self):
        return [ProfileSuggestion("id", "x", "x", "x", "x")]


class Tabs(horizon.tabs.TabGroup):
    tabs = (
        NodeProfiles,
        ProfileSuggestions,
    )
    sticky = True
