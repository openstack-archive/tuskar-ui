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


def filter_items(items, **kwargs):
    """Filters the list of items and returns the filtered list.

    Example usage:
    >>> filter_items(nodes, power_state='error')
    >>> filter_items(nodes, power_state__in=('on', 'power on'))
    """
    for item in items:
        for name, value in kwargs.items():
            if name.endswith('__in'):
                if getattr(item, name[:-len('__in')]) not in value:
                    break
            elif name.endswith('__not_in'):
                if getattr(item, name[:-len('__not_in')]) in value:
                    break
            else:
                if getattr(item, name) != value:
                    break
        else:
            yield item
