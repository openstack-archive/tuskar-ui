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

# from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud.workflows import scale_node_counts
from tuskar_ui.infrastructure.overcloud.workflows import undeployed


class Workflow(undeployed.DeploymentValidationMixin,
               horizon.workflows.Workflow):
    slug = 'scale_overcloud'
    name = _("Scale Deployment")
    default_steps = (
        scale_node_counts.Step,
    )
    finalize_button_name = _("Apply Changes")

    def handle(self, request, context):
        # overcloud_id = self.context['overcloud_id']
        try:
            # TODO(rdopieralski) Actually update it when possible.
            # overcloud = api.Overcloud.get(request, overcloud_id)
            # overcloud.update(self.request, context['role_counts'])
            pass
        except Exception:
            exceptions.handle(request, _('Unable to update deployment.'))
            return False
        return True

    def get_success_url(self):
        overcloud_id = self.context.get('overcloud_id', 1)
        return reverse('horizon:infrastructure:overcloud:detail',
                       args=(overcloud_id,))
