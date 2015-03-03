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

import json

from django import template


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

    return json.dumps(all_used_instances_info)


@register.filter()
def ellipsis(s, n):
    """Shorten a long string.

    :param s: string to shorten
    :param n: number of charto keep on both sides
    :return: shotened string
    """
    n = int(n)
    if len(s) <= 2 * n:
        return s
    return s[:n]+'...'+s[-n:]
