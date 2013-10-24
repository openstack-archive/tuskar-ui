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

import re

from django.forms import fields
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _  # noqa


class NumberInput(widgets.TextInput):
    input_type = 'number'


class MACField(fields.RegexField):
    MAC_RE = re.compile(
        r'^\s*[0-9a-fA-F]{2}([.:-])([0-9a-fA-F]{2}\1){4}[0-9a-fA-F]{2}\s*$')
    default_error_messages = {'invalid': _(u'Enter a valid MAC address.')}

    def __init__(self, *args, **kwargs):
        super(MACField, self).__init__(self.MAC_RE, *args, **kwargs)

    def clean(self, value):
        value = super(MACField, self).clean(value).upper()
        digits = [c for c in value if c in '0123456789ABCDEF']
        return ':'.join(''.join(cc) for cc in zip(digits[::2], digits[1::2]))
