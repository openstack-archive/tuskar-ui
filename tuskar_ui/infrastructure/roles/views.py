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
import json

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django import http
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base
from glanceclient import exc as glance_exc
from horizon import exceptions as horizon_exceptions
from horizon import tables as horizon_tables
from horizon import utils
from horizon import workflows
from openstack_dashboard.api import base as api_base

from tuskar_ui import api
from tuskar_ui.infrastructure.roles import tables
from tuskar_ui.infrastructure.roles import workflows as role_workflows
from tuskar_ui.infrastructure import views
from tuskar_ui.utils import metering as metering_utils


INDEX_URL = 'horizon:infrastructure:roles:index'


class IndexView(views.ItemCountMixin, horizon_tables.DataTableView):
    table_class = tables.RolesTable
    template_name = "infrastructure/roles/index.html"

    @utils.memoized.memoized
    def get_data(self):
        roles = api.tuskar.Role.list(self.request)
        plan = api.tuskar.Plan.get_the_plan(self.request)
        for role in roles:
            role_flavor = role.flavor(plan)
            try:
                role_image = role.image(plan)
            except glance_exc.HTTPNotFound:
                # Glance returns a 404 if the image doesn't exist
                role_image = None
            if role_flavor:
                role.flavor = role_flavor.name
            else:
                role.flavor = _('Unknown')
            if role_image:
                role.image = role_image.name
            else:
                role.image = _('Unknown')

        return roles


class DetailView(horizon_tables.DataTableView, views.RoleMixin,
                 views.StackMixin):
    table_class = tables.NodeTable
    template_name = 'infrastructure/roles/detail.html'

    @utils.memoized.memoized
    def _get_nodes(self, stack, role):
        resources = stack.resources(role=role, with_joins=True)
        nodes = [r.node for r in resources]
        for node in nodes:
            try:
                resource = api.heat.Resource.get_by_node(self.request, node)
            except LookupError:
                node.role_name = '-'
            else:
                node.role_name = resource.role.name
                node.role_id = resource.role.id
                node.stack_id = resource.stack.id

        return nodes

    def get_data(self):
        redirect = reverse(INDEX_URL)
        stack = self.get_stack()
        if stack:
            role = self.get_role(redirect)
            return self._get_nodes(stack, role)
        return []

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        redirect = reverse(INDEX_URL)

        plan = api.tuskar.Plan.get_the_plan(self.request)
        stack = self.get_stack()
        role = self.get_role(redirect)

        context['role'] = role
        if stack:
            context['nodes'] = self._get_nodes(stack, role)
        else:
            context['nodes'] = []
        context['flavor'] = role.flavor(plan)
        context['image'] = role.image(plan)

        if stack:
            if api_base.is_service_enabled(self.request, 'metering'):
                # Meter configuration in the following format:
                # (meter label, url part, barchart (True/False))
                context['meter_conf'] = (
                    (_('System Load'),
                     metering_utils.url_part('hardware.cpu.load.1min', False),
                     None),
                    (_('CPU Utilization'),
                     metering_utils.url_part('hardware.system_stats.cpu.util',
                                             True),
                     '100'),
                    (_('Swap Utilization'),
                     metering_utils.url_part('hardware.memory.swap.util',
                                             True),
                     '100'),
                )
        return context


class UpdateView(workflows.WorkflowView, views.StackMixin, views.RoleMixin):
    workflow_class = role_workflows.UpdateRole

    def get_initial(self):
        plan = self.get_plan()
        role = self.get_role()

        stack = self.get_stack()
        if stack:
            resources = stack.resources(role=role, with_joins=True)
            role_nodes = len(resources)
        else:
            role_nodes = 0

        role_flavor = role.flavor(plan)
        role_flavor = '' if role_flavor is None else role_flavor.name

        role_image = role.image(plan)
        role_image = '' if role_image is None else role_image.id

        free_nodes = len(api.node.Node.list(self.request, associated=False,
                                            maintenance=False))
        available_nodes = role_nodes + free_nodes

        return {
            'role_id': role.id,
            'name': role.name,
            'flavor': role_flavor,
            'image': role_image,
            'nodes': role_nodes,
            'available_nodes': available_nodes,
        }


class PerformanceView(base.TemplateView, views.RoleMixin, views.StackMixin):
    def get(self, request, *args, **kwargs):
        meter = request.GET.get('meter')
        date_options = request.GET.get('date_options')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        stats_attr = request.GET.get('stats_attr', 'avg')
        barchart = bool(request.GET.get('barchart'))

        plan = api.tuskar.Plan.get_the_plan(self.request)
        role = self.get_role(None)
        role.image(plan)

        try:
            image = role.image(plan)
            image_uuid = image.id
        except AttributeError:
            json_output = None
        else:
            json_output = metering_utils.get_nodes_stats(
                request, image_uuid, meter, date_options=date_options,
                date_from=date_from, date_to=date_to, stats_attr=stats_attr,
                barchart=barchart, group_by='image_id')

        return http.HttpResponse(json.dumps(json_output),
                                 mimetype='application/json')
