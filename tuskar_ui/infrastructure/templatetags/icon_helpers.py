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

from django import template
from django.utils.translation import ugettext_lazy as _


register = template.Library()

IRONIC_NODE_STATE_STRING_DICT = {
    'active': _('powered on'),
    'wait call-back': _('waiting'),
    'deploying': _('deploying'),
    'deploy failed': _('deployment failed'),
    'deploy complete': _('deployment complete'),
    'deleting': _('deleting'),
    'deleted': _('deleted'),
    'error': _('error'),
    'rebuild': _('rebuilding'),
    'power on': _('powered on'),
    'power off': _('powered off'),
    'rebooting': _('rebooting'),
}

IRONIC_NODE_STATE_ICON_DICT = {
    'active': 'fa-play',
    'wait call-back': 'fa-spinner',
    'deploying': 'fa-spinner',
    'deploy failed': 'fa-warning',
    'deploy complete': 'fa-ok',
    'deleting': 'fa-spinner',
    'deleted': 'fa-cancel',
    'error': 'fa-warning',
    'rebuild': 'fa-spinner',
    'power on': 'fa-play',
    'power off': 'fa-stop',
    'rebooting': 'fa-spinner',
}


@register.filter(is_safe=True)
def iconized_ironic_node_state(node_power_state):
    state = IRONIC_NODE_STATE_STRING_DICT.get(node_power_state, "&mdash;")
    icon = IRONIC_NODE_STATE_ICON_DICT.get(node_power_state, 'fa-question')
    html_string = (u"""<span class="fa %s powerstate"></span>"""
                   u"""<span>%s</span> """) % (icon, unicode(state))

    return html_string
