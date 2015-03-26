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
import csv
from itertools import izip
import re

from django.utils.translation import ugettext_lazy as _

CAMEL_RE = re.compile(r'([A-Z][a-z]+|[A-Z]+(?=[A-Z\s]|$))')


def de_camel_case(text):
    """Convert CamelCase names to human-readable format."""
    return ' '.join(w.strip() for w in CAMEL_RE.split(text) if w.strip())


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
    """Check if image 'type' property matches passed-in type.

    If image has no 'type' property' return True, as we cannot
    be sure what type of image it is.
    """

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


def safe_int_cast(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_csv_file(csv_file):
    """Parses given CSV file.

    If there is no error, it returns list of dicts. When something went wrong,
    list is empty, but warning contains appropriate information about
    possible problems.
    """

    parsed_data = []

    for row in csv.reader(csv_file):
        try:
            driver = row[0].strip()
        except IndexError:
            raise ValueError(_("Unable to parse the CSV file."))

        if driver in ('pxe_ssh', 'pxe_ipmitool'):
            node_keys = (
                'mac_addresses', 'cpu_arch', 'cpus', 'memory_mb', 'local_gb')

            if driver == 'pxe_ssh':
                driver_keys = (
                    'driver', 'ssh_address', 'ssh_username',
                    'ssh_key_contents'
                )

            elif driver == 'pxe_ipmitool':
                driver_keys = (
                    'driver', 'ipmi_address', 'ipmi_username',
                    'ipmi_password'
                )

            node = dict(izip(driver_keys+node_keys, row))

            parsed_data.append(node)

        else:
            raise ValueError(_("Unknown driver: %s.") % driver)

    return parsed_data
