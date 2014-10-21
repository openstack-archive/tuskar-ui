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
import re

CAMEL_RE = re.compile(r'([a-z]|SSL)([A-Z])')


def de_camel_case(text):
    """Convert CamelCase names to human-readable format."""
    return CAMEL_RE.sub(lambda m: m.group(1) + ' ' + m.group(2), text)


def list_to_dict(object_list, key_attribute='id'):
    """Converts an object list to a dict

    :param object_list: list of objects to be put into a dict
    :type  object_list: list

    :param key_attribute: object attribute used as index by dict
    :type  key_attribute: str

    :return: dict containing the objects in the list
    :rtype: dict
    """
    return dict((getattr(o, key_attribute), o) for o in object_list)


def length(iterator):
    """A length function for iterators

    Returns the number of items in the specified iterator. Note that this
    function consumes the iterator in the process.
    """
    return sum(1 for _item in iterator)


def check_image_type(image, type):
    return (image.properties.get('type', type) == type)


def filter_items(items, **kwargs):
    """Filters the list of items and returns the filtered list.

    Example usage:
    >>> class Item(object):
    ...     def __init__(self, index):
    ...         self.index = index
    ...     def __repr__(self):
    ...         return '<Item index=%d>' % self.index
    >>> items = [Item(i) for i in range(7)]
    >>> list(filter_items(items, index=1))
    [<Item index=1>]
    >>> list(filter_items(items, index__in=(1, 2, 3)))
    [<Item index=1>, <Item index=2>, <Item index=3>]
    >>> list(filter_items(items, index__not_in=(1, 2, 3)))
    [<Item index=0>, <Item index=4>, <Item index=5>, <Item index=6>]
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
