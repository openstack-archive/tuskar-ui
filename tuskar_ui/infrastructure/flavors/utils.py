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

from django.conf import settings

from tuskar_ui import api


def matching_deployment_mode():
    deployment_mode = getattr(settings, 'DEPLOYMENT_MODE', 'scale')
    return deployment_mode.lower() == 'scale'


def _safe_int_cast(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


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
            vcpus=_safe_int_cast(node.cpus),
            ram=_safe_int_cast(node.memory_mb),
            disk=_safe_int_cast(node.local_gb),
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

    def create_flavor(self, request):
        return api.flavor.Flavor.create(
            request,
            name=self.name,
            memory=self.ram,
            vcpus=self.vcpus,
            disk=self.disk,
            cpu_arch=self.cpu_arch,
            # TODO(rdopieralski) Should we use some defaults here? What?
            kernel_image_id='',
            ramdisk_image_id='',
        )
