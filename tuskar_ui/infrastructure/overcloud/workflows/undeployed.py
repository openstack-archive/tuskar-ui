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
from django.core import exceptions as django_exceptions
from django.utils.translation import ugettext_lazy as _

import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud.workflows\
    import undeployed_configuration
from tuskar_ui.infrastructure.overcloud.workflows import undeployed_overview


class Workflow(horizon.workflows.Workflow):
    slug = 'undeployed_overcloud'
    name = _("My OpenStack Deployment")
    default_steps = (
        undeployed_overview.Step,
        undeployed_configuration.Step,
    )
    finalize_button_name = _("Deploy")
    success_url = 'horizon:infrastructure:overcloud:index'

    def handle(self, request, context):
        try:
            api.Overcloud.create(self.request, context['role_counts'],
                                 context['configuration'])
        except Exception as e:
            # Showing error in both workflow tabs, because from the exception
            # type we can't recognize where it should show
            self.add_error_to_step(e.message, 'undeployed_overview')
            self.add_error_to_step(e.message, 'deployed_configuration')
            raise django_exceptions.ValidationError(e.message)

        return True
