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
from horizon import tabs as horizon_tabs
import horizon.workflows

from tuskar_ui import api
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
