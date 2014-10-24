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


register = template.Library()

IRONIC_NODE_STATE_STRING_DICT = {
    'active': 'powered on',
    'wait call-back': 'waiting',
    'deploying': 'deploying',
    'deploy failed': 'deployment failed',
    'deploy complete': 'deployment complete',
    'deleting': 'deleting',
    'deleted': 'deleted',
    'error': 'error',
    'rebuild': 'rebuilding',
    'power on': 'powered on',
    'power off': 'powered off',
    'rebooting': 'rebooting',
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
    icon = IRONIC_NODE_STATE_ICON_DICT.get(node_power_state, None)
    html_string = """<span class="fa %s powerstate"></span>
                     <span>%s</span> """ % (icon, state)

    return html_string
