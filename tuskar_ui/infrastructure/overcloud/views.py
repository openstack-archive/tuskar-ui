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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import base as base_views

from horizon import exceptions
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs
from horizon.utils import memoized
import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud import tables
from tuskar_ui.infrastructure.overcloud import tabs
from tuskar_ui.infrastructure.overcloud.workflows import undeployed


class IndexView(base_views.RedirectView):
    permanent = False

    def get_redirect_url(self):
        overcloud = api.Overcloud.get(self.request, 1)
        if overcloud is not None and overcloud.is_deployed:
            redirect = reverse('horizon:infrastructure:overcloud:detail',
                               args=(overcloud.id,))
        else:
            redirect = reverse('horizon:infrastructure:overcloud:create')
        return redirect


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = undeployed.Workflow
    template_name = 'infrastructure/_fullscreen_workflow_base.html'


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.DetailTabs
    template_name = 'infrastructure/overcloud/detail.html'

    def get_data(self, request, **kwargs):
        overcloud_id = kwargs['overcloud_id']
        try:
            return api.Overcloud.get(request, overcloud_id)
        except Exception:
            msg = _("Unable to retrieve deployment.")
            redirect = reverse('horizon:infrastructure:overcloud:index')
            exceptions.handle(request, msg, redirect=redirect)

    def get_tabs(self, request, **kwargs):
        overcloud = self.get_data(request, **kwargs)
        return self.tab_group_class(request, overcloud=overcloud, **kwargs)


class ResourceCategoryView(horizon_tables.DataTableView):
    table_class = tables.ResourceCategoryNodeTable
    template_name = 'infrastructure/overcloud/resource_category.html'

    def get_data(self):
        overcloud = self._get_overcloud()
        category = self._get_category(overcloud)

        return self._get_nodes(overcloud, category)

    def get_context_data(self, **kwargs):
        context = super(ResourceCategoryView, self).get_context_data(**kwargs)

        overcloud = self._get_overcloud()
        category = self._get_category(overcloud)

        context['category'] = category
        context['image'] = category.image
        context['nodes'] = self._get_nodes(overcloud, category)

        return context

    @memoized.memoized
    def _get_nodes(self, overcloud, category):
        resources = overcloud.resources(category, with_joins=True)
        return [r.node for r in resources]

    @memoized.memoized
    def _get_overcloud(self):
        overcloud_id = self.kwargs['overcloud_id']

        try:
            overcloud = api.Overcloud.get(self.request, overcloud_id)
        except Exception:
            msg = _("Unable to retrieve deployment.")
            redirect = reverse('horizon:infrastructure:overcloud:index')
            exceptions.handle(self.request, msg, redirect=redirect)

        return overcloud

    @memoized.memoized
    def _get_category(self, overcloud):
        category_id = self.kwargs['category_id']

        try:
            category = api.ResourceCategory.get(self.request, category_id)
        except Exception:
            msg = _("Unable to retrieve resource category.")
            redirect = reverse('horizon:infrastructure:overcloud:detail',
                               args=(overcloud.id,))
            exceptions.handle(self.request, msg, redirect=redirect)

        return category
