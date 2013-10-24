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

from django import forms
from django.utils.translation import ugettext_lazy as _  # noqa
import netaddr


class NumberInput(forms.widgets.TextInput):
    input_type = 'number'


class MACField(forms.fields.Field):
    def clean(self, value):
        try:
            return str(netaddr.EUI(
                value, version=48, dialect=netaddr.mac_unix)).upper()
        except netaddr.AddrFormatError:
            raise forms.ValidationError(_(u'Enter a valid MAC address.'))


class NetworkField(forms.fields.Field):
    def clean(self, value):
        try:
            return str(netaddr.IPNetwork(value, version=4))
        except netaddr.AddrFormatError:
            raise forms.ValidationError(_("Enter valid IPv4 network address."))
