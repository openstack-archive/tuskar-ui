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
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
import horizon.workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.overcloud.workflows\
    import undeployed_configuration
from tuskar_ui.infrastructure.overcloud.workflows import undeployed_overview


LOG = logging.getLogger(__name__)


class DeploymentValidationMixin(object):
    def validate(self, context):
        requested = sum(context['role_counts'].values())
        # TODO(lsmola) change this when we support more overclouds. It
        # will have to obtain actual free nodes and compare them to
        # number of newly created.
        free = len(api.node.Node.list(self.request))
        if requested > free:
            m1 = translation.ungettext_lazy(
                'This configuration requires %(requested)d node, ',
                'This configuration requires %(requested)d nodes, ',
                requested)
            m1 %= {'requested': requested}
            m2 = translation.ungettext_lazy(
                'but only %(free)d is available.',
                'but only %(free)d are available.',
                free)
            m2 %= {'free': free}
            message = unicode(translation.string_concat(m1, m2))
            self.add_error_to_step(message, 'undeployed_overview')
            self.add_error_to_step(message, 'scale_node_counts')
            return False
        return super(DeploymentValidationMixin, self).validate(context)


class Workflow(DeploymentValidationMixin, horizon.workflows.Workflow):
    slug = 'undeployed_overcloud'
    name = _("My OpenStack Deployment")
    default_steps = (
        undeployed_overview.Step,
        undeployed_configuration.Step,
    )
    finalize_button_name = _("Deploy")
    success_message = _("OpenStack deployment launched")
    success_url = 'horizon:infrastructure:overcloud:index'

    def handle(self, request, context):
        try:
            api.tuskar.OvercloudPlan.create(
                self.request, context['role_counts'],
                context['configuration'])
        except Exception as e:
            # Showing error in both workflow tabs, because from the exception
            # type we can't recognize where it should show
            msg = unicode(e)
            self.add_error_to_step(msg, 'undeployed_overview')
            self.add_error_to_step(msg, 'deployed_configuration')
            LOG.exception('Error creating overcloud')
            raise django.forms.ValidationError(msg)
        return True
