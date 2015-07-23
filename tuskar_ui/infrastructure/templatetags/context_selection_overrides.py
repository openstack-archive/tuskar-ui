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

from __future__ import absolute_import

from django import template


register = template.Library()

# Overwrite the selector code from OpenStack Dashboard, so that the
# selector doesn't appear.


@register.simple_tag()
def show_overview(*args, **kwargs):
    return '<span class="context-overview"></span>'


@register.simple_tag()
def show_domain_list(*args, **kwargs):
    return ''


@register.simple_tag()
def show_project_list(*args, **kwargs):
    return ''


@register.simple_tag()
def show_region_list(*args, **kwargs):
    return ''
