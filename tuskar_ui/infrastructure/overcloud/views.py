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
from django.views.generic import base as base_views

import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud.workflows import deployed
from tuskar_ui.infrastructure.overcloud.workflows import undeployed


class IndexView(base_views.RedirectView):
    permanent = False

    def get_redirect_url(self):
        overcloud = api.Overcloud.get(self.request)
        if overcloud is not None and overcloud.is_deployed:
            redirect = reverse('horizon:infrastructure:overcloud:detail',
                               args=(overcloud.id,))
        else:
            redirect = reverse('horizon:infrastructure:overcloud:create')
        return redirect


class CreateView(horizon.workflows.WorkflowView):
    workflow_class = undeployed.Workflow
    template_name = 'infrastructure/_fullscreen_workflow_base.html'


class DetailView(horizon.workflows.WorkflowView):
    workflow_class = deployed.Workflow
    template_name = 'infrastructure/_fullscreen_workflow_base.html'
