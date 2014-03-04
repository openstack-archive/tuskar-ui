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

import django.forms
from django.utils.translation import ugettext_lazy as _
import horizon.workflows

from tuskar_ui.infrastructure.overcloud.workflows import undeployed_overview


class Action(undeployed_overview.Action):
    overcloud_id = django.forms.IntegerField(widget=django.forms.HiddenInput)

    class Meta:
        slug = 'scale_node_counts'
        name = _("Node Counts")


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ('role_counts', 'overcloud_id')
    template_name = 'infrastructure/overcloud/scale_node_counts.html'

    def prepare_action_context(self, request, context):
        for (role_id, profile_id), count in context['role_counts'].items():
            name = 'count__%s__%s' % (role_id, profile_id)
            context[name] = count
        return context

    def contribute(self, data, context):
        counts = {}
        for key, value in data.iteritems():
            if not key.startswith('count_'):
                continue
            count, role_id, profile = key.split('__', 2)
            counts[role_id, profile] = int(value)
        context['role_counts'] = counts
        return context
