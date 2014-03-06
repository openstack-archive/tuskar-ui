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
from tuskar_ui.infrastructure.node_profiles import tables


def _get_unmatched_nodes(request):
    node_profiles = api.NodeProfile.list(request)
    all_nodes = api.Node.list(request)
    unmatched_nodes = []
    for node in all_nodes:
        for node_profile in node_profiles:
            if (
                ProfileSuggestion.from_node_profile(node_profile) ==
                ProfileSuggestion.from_node(node)
            ):
                break
        else:
            unmatched_nodes.append(node)
    return unmatched_nodes


def get_profile_suggestions(request):
    return set(ProfileSuggestion.from_node(node)
               for node in _get_unmatched_nodes(request))


class NodeProfilesTab(horizon.tabs.TableTab):
    name = _("Node Profiles")
    slug = 'node_profiles'
    table_classes = (tables.NodeProfilesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_node_profiles_data(self):
        node_profiles = api.NodeProfile.list(self.request)
        node_profiles.sort(key=lambda np: (np.vcpus, np.ram, np.disk))
        return node_profiles


class ProfileSuggestion(object):
    """Describe node parameters in a way that is easy to compare."""

    def __init__(self, vcpus=None, ram=None, disk=None, cpu_arch=None):
        self.vcpus = vcpus
        self.ram = ram
        self.disk = disk
        self.cpu_arch = cpu_arch

    @classmethod
    def from_node(cls, node):
        return cls(
            vcpus=node.properties['cpu'],
            ram=int(node.properties['ram']),
            disk=int(node.properties['local_disk']),
            # TODO(rdopieralski) Add architecture when available.
        )

    @classmethod
    def from_node_profile(cls, node_profile):
        return cls(
            vcpus=node_profile.vcpus,
            ram=node_profile.ram * 1024 * 1024,
            disk=node_profile.disk * 1024 * 1024 * 1024,
            # TODO(rdopieralski) Add architecture when available.
        )

    @property
    def id(self):
        return '%s-%s-%s-%s' % (self.vcpus, self.ram, self.disk, self.cpu_arch)

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '%s(vcpus=%r, ram=%r, disk=%r, cpu_arch=%r)' % (
            self.__class__.__name__,
            self.vcpus,
            self.ram,
            self.disk,
            self.cpu_arch,
        )


class ProfileSuggestionsTab(horizon.tabs.TableTab):
    name = _("Profile Suggestions")
    slug = 'profile_suggestions'
    table_classes = (tables.ProfileSuggestionsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_profile_suggestions_data(self):
        return list(get_profile_suggestions(self.request))


class NodeProfileTabs(horizon.tabs.TabGroup):
    slug = 'node_profile_tabs'
    tabs = (
        NodeProfilesTab,
        ProfileSuggestionsTab,
    )
    sticky = True
