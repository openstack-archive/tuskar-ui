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
import logging

import django.forms
from django.utils.translation import ugettext_lazy as _
import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.plans.workflows import create_configuration
from tuskar_ui.infrastructure.plans.workflows import create_overview


LOG = logging.getLogger(__name__)


class Workflow(horizon.workflows.Workflow):
    slug = 'create_plan'
    name = _("My OpenStack Deployment Plan")
    default_steps = (
        create_overview.Step,
        create_configuration.Step,
    )
    finalize_button_name = _("Deploy")
    success_message = _("OpenStack deployment launched")
    success_url = 'horizon:infrastructure:overcloud:index'

    def handle(self, request, context):
        try:
            api.tuskar.OvercloudPlan.create(
                self.request, 'overcloud', 'overcloud')
        except Exception as e:
            # Showing error in both workflow tabs, because from the exception
            # type we can't recognize where it should show
            msg = unicode(e)
            self.add_error_to_step(msg, 'create_overview')
            self.add_error_to_step(msg, 'create_configuration')
            LOG.exception('Error creating overcloud plan')
            raise django.forms.ValidationError(msg)
        return True
