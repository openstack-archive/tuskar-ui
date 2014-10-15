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


def _get_unmatched_suggestions(request):
    unmatched_suggestions = []
    flavor_suggestions = [FlavorSuggestion.from_flavor(flavor)
                          for flavor in api.flavor.Flavor.list(request)]
    for node in api.node.Node.list(request):
        node_suggestion = FlavorSuggestion.from_node(node)
        for flavor_suggestion in flavor_suggestions:
            if flavor_suggestion == node_suggestion:
                break
        else:
            unmatched_suggestions.append(node_suggestion)
    return unmatched_suggestions


def get_flavor_suggestions(request):
    return set(_get_unmatched_suggestions(request))


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


class FlavorSuggestion(object):
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
            node_id=node.uuid,
            vcpus=int(node.cpus),
            ram=int(node.memory_mb),
            disk=int(node.local_gb),
            cpu_arch=node.cpu_arch
        )

    @classmethod
    def from_flavor(cls, flavor):
        return cls(
            vcpus=flavor.vcpus,
            ram_bytes=flavor.ram_bytes,
            disk_bytes=flavor.disk_bytes,
            cpu_arch=flavor.cpu_arch
        )

    @property
    def name(self):
        return 'Flavor-%scpu-%s-%sMB-%sGB' % (
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


class FlavorSuggestionsTab(horizon.tabs.TableTab):
    name = _("Suggested")
    slug = 'flavor_suggestions'
    table_classes = (tables.FlavorSuggestionsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_items_count(self):
        return len(self.get_flavor_suggestions_data())

    def get_flavor_suggestions_data(self):
        return list(get_flavor_suggestions(self.request))


class FlavorTabs(horizon.tabs.TabGroup):
    slug = 'flavor_tabs'
    tabs = (
        FlavorsTab,
        FlavorSuggestionsTab,
    )
    sticky = True
    template_name = "horizon/common/_items_count_tab_group.html"
