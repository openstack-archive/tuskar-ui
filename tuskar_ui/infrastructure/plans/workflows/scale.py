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
from horizon import exceptions
import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.plans.workflows import create
from tuskar_ui.infrastructure.plans.workflows import scale_node_counts


class Workflow(create.DeploymentValidationMixin,
               horizon.workflows.Workflow):
    slug = 'scale_overcloud'
    name = _("Scale Deployment")
    default_steps = (
        scale_node_counts.Step,
    )
    finalize_button_name = _("Apply Changes")

    def handle(self, request, context):
        plan_id = context['plan_id']
        try:
            # TODO(lsmola) when updates are fixed in Heat, figure out whether
            # we need to send also parameters, right now we send {}
            api.tuskar.OvercloudPlan.update(request, plan_id,
                                            context['role_counts'], {})
        except Exception:
            exceptions.handle(request, _('Unable to update deployment.'))
            return False
        return True

    def get_success_url(self):
        plan_id = self.context.get('plan_id', 1)
        return reverse('horizon:infrastructure:overcloud:detail',
                       args=(plan_id,))
