# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from django.utils.translation import ugettext_lazy as _  # noqa

import horizon


class InfrastructureOverview(horizon.PanelGroup):
    slug = "infrastructure_overview"
    name = _("Overview")
    panels = (
        'overview',
    )


class Deployment(horizon.PanelGroup):
    slug = "deploy"
    name = _("Deployment")
    panels = (
        'deploy_overview',
        'deploy_controller',
        'deploy_compute',
        'deploy_object_storage',
        'deploy_block_storage',
    )


class Resources(horizon.PanelGroup):
    slug = "nodes"
    name = _("Resources")
    panels = (
        'resources_overview',
        'resources_resource',
        'resources_management',
        'resources_unallocated',
        'resources_archived',
    )


class Infrastructure(horizon.Dashboard):
    name = _("Infrastructure")
    slug = "infrastructure"
    panels = (
        InfrastructureOverview,
        Deployment,
        Resources,
    )
    default_panel = 'overview'
    permissions = ('openstack.roles.admin',)


horizon.register(Infrastructure)
