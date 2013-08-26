# vim: tabstop=4 shiftwidth=4 softtabstop=4
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
from django.utils import simplejson

register = template.Library()


@register.filter()
def remaining_capacity_by_flavors(obj):
    flavors = obj.list_flavors

    decorated_obj = " ".join(
        [("<p><strong>{0}</strong> {1}</p>").format(
            str(flavor.used_instances),
            flavor.name)
            for flavor in flavors])

    decorated_obj = ("<p>Capacity remaining by flavors: </p>" +
                     decorated_obj)

    return decorated_obj


@register.filter()
def all_used_instances(obj):
    flavors = obj.list_flavors

    all_used_instances_info = []
    for flavor in flavors:
        info = {}
        info['popup_used'] = (
            '<p> {0}% total,'
            ' <strong> {1} instances</strong> of {2}</p>'.format(
            flavor.used_instances,
            flavor.used_instances,
            flavor.name))
        info['used_instances'] = str(flavor.used_instances)

        all_used_instances_info.append(info)

    return simplejson.dumps(all_used_instances_info)
