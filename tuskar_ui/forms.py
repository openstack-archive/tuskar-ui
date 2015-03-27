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

from django import forms
from django.utils import html
from django.utils.translation import ugettext_lazy as _
import netaddr


SEPARATOR_RE = re.compile('[\s,;|]+', re.UNICODE)


def label_with_tooltip(label, tooltip=None, title=None):
    if not tooltip:
        return label
    return html.format_html(
        u'{0}&nbsp;<a class="help-icon fa fa-question-circle" '
        u'data-content="{1}" tabindex="0" href="#" '
        u'data-title="{2}"></a>',
        html.escape(label),
        html.escape(tooltip),
        html.escape(title or label)
    )


def fieldset(form, *args, **kwargs):
    """A helper function for grouping fields based on their names."""

    prefix = kwargs.pop('prefix', '.*')
    names = args or form.fields.keys()

    for name in names:
        if prefix is not None and re.match(prefix, name):
            yield forms.forms.BoundField(form, form.fields[name], name)


class MACDialect(netaddr.mac_eui48):
    """For validating MAC addresses. Same validation as Nova uses."""
    word_fmt = '%.02x'
    word_sep = ':'


def normalize_MAC(value):
    try:
        return str(netaddr.EUI(
            value.strip(), version=48, dialect=MACDialect)).upper()
    except (netaddr.AddrFormatError, TypeError):
        raise ValueError('Invalid MAC address')


class NumberInput(forms.widgets.TextInput):
    """A form input for numbers."""
    input_type = 'number'


class NumberPickerInput(forms.widgets.TextInput):
    """A form input that is rendered as a big number picker."""

    def __init__(self, attrs=None):
        default_attrs = {'class': 'number-picker'}
        if attrs:
            default_attrs.update(attrs)
        super(NumberPickerInput, self).__init__(default_attrs)


class MACField(forms.fields.Field):
    """A form field for entering a single MAC address."""

    def clean(self, value):
        value = super(MACField, self).clean(value)
        try:
            return normalize_MAC(value)
        except ValueError:
            raise forms.ValidationError(_(u'Enter a valid MAC address.'))


class MultiMACField(forms.fields.Field):
    """A form field for entering multiple MAC addresses.

       The individual MAC addresses can be separated by any whitespace,
       commas, semicolons or pipe characters.

       Gives a string of normalized MAC addresses separated by spaces.
    """

    def clean(self, value):
        value = super(MultiMACField, self).clean(value)

        macs = []
        for mac in SEPARATOR_RE.split(value):
            if mac:
                try:
                    normalized_mac = normalize_MAC(mac)
                except ValueError:
                    raise forms.ValidationError(
                        _(u'%r is not a valid MAC address.') % mac)
                else:
                    macs.append(normalized_mac)

        return ' '.join(sorted(set(macs)))


class NetworkField(forms.fields.Field):
    """A form field for entering a network specification with a mask."""

    def clean(self, value):
        value = super(NetworkField, self).clean(value)
        try:
            return str(netaddr.IPNetwork(value, version=4))
        except netaddr.AddrFormatError:
            raise forms.ValidationError(_("Enter valid IPv4 network address."))


class SelfHandlingFormset(forms.formsets.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SelfHandlingFormset, self).__init__(*args, **kwargs)

    def handle(self, request, data):
        success = True
        for form in self:
            form_success = form.handle(request, form.cleaned_data)
            if not form_success:
                success = False
            else:
                pass
        return success


class LabelWidget(forms.Widget):
    """A widget for displaying information.

    This is a custom widget to show context information just as text,
    as readonly inputs are confusing.
    Note that the field also must be required=False, as no input
    is rendered, and it must be ignored in the handle() method.
    """
    def render(self, name, value, attrs=None):
        if value:
            return html.escape(value)
        return ''


class StaticTextWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return html.format_html('<p class="form-control-static">{0}</p>',
                                value)


class StaticTextPasswordWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        if value is None or value == '':
            return html.format_html(u'<p class="form-control-static"></p>')
        else:
            return html.format_html(
                u'<p class="form-control-static">'
                u'<a href="" class="btn btn-default btn-xs password-button"'
                u' data-content="{0}"><i class="fa fa-eye"></i>&nbsp;{1}</a>'
                u'</p>', value, _(u"Reveal")
            )
