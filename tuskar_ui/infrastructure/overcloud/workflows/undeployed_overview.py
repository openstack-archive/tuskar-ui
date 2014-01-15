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


class Action(horizon.workflows.Action):
    controller = django.forms.IntegerField(_("Controller"))
    compute = django.forms.IntegerField(_("Compute"))
    object_storage = django.forms.IntegerField(_("Object Storage"))
    block_storage = django.forms.IntegerField(_("Block Storage"))

    class Meta:
        slug = 'undeployed_overview'
        name = _("Overview")


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ()
    template_name = 'infrastructure/overcloud/undeployed-overview.html'
    help_text = _("Nothing deployed yet. Design your first deployment.")
