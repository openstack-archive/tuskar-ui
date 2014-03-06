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


def _get_unmatched_suggestions(request):
    unmatched_suggestions = []
    profile_suggestions = [ProfileSuggestion.from_node_profile(node_profile)
                           for node_profile in api.NodeProfile.list(request)]
    for node in api.Node.list(request):
        node_suggestion = ProfileSuggestion.from_node(node)
        for profile_suggestion in profile_suggestions:
            if profile_suggestion == node_suggestion:
                break
        else:
            unmatched_suggestions.append(node_suggestion)
    return unmatched_suggestions


def get_profile_suggestions(request):
    return set(_get_unmatched_suggestions(request))


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

    def __init__(self, vcpus=None, ram=None, disk=None, cpu_arch=None,
                 ram_bytes=None, disk_bytes=None, node_id=None):
        self.vcpus = vcpus
        self.ram_bytes = ram_bytes or ram * 1024 * 1024 or 0
        self.disk_bytes = disk_bytes or disk * 1024 * 1024 * 1024 or 0
        self.cpu_arch = cpu_arch
        self.id = node_id

    @classmethod
    def from_node(cls, node):
        return cls(
            node_id=node.id,
            vcpus=int(node.properties['cpu']),
            ram_bytes=int(node.properties['ram']),
            disk_bytes=int(node.properties['local_disk']),
            # TODO(rdopieralski) Add architecture when available.
        )

    @classmethod
    def from_node_profile(cls, node_profile):
        return cls(
            vcpus=node_profile.vcpus,
            ram_bytes=node_profile.ram_bytes,
            disk_bytes=node_profile.disk_bytes,
            # TODO(rdopieralski) Add architecture when available.
        )

    @property
    def name(self):
        return '%s-%s-%s-%s' % (
            self.vcpus or '0',
            self.cpu_arch or '',
            self.ram or '0',
            self.disk or '0',
        )

    @property
    def ram(self):
        return self.ram_bytes / 1024 / 1024

    @property
    def disk(self):
        return self.disk_bytes / 1024 / 1024 / 1024

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return (
            '%s(vcpus=%r, ram_bytes=%r, disk_bytes=%r, '
            'cpu_arch=%r, node_id=%r)' % (
                self.__class__.__name__,
                self.vcpus,
                self.ram_bytes,
                self.disk_bytes,
                self.cpu_arch,
                self.id,
            )
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
