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

from django.utils.translation import ugettext_lazy as _

from tuskar_ui.infrastructure.overcloud.workflows import undeployed_overview


class Action(undeployed_overview.Action):
    class Meta:
        slug = 'scale_node_counts'
        name = _("Node Counts")


class Step(undeployed_overview.Step):
    action_class = Action
    contributes = ('role_counts', 'plan_id')
    template_name = 'infrastructure/overcloud/scale_node_counts.html'

    def prepare_action_context(self, request, context):
        for (role_id, flavor_id), count in context['role_counts'].items():
            name = 'count__%s__%s' % (role_id, flavor_id)
            context[name] = count
        return context
