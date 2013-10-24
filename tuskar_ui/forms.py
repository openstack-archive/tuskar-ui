import re

import django.forms
from django.forms import fields
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _  # noqa


class NumberInput(widgets.TextInput):
    input_type = 'number'


class NetworkField(fields.RegexField):
    NET_RE = re.compile(
        r'^\s*([1-2]?[0-9]?[0-9][.]){3}[1-2]?[0-9]?[0-9][/][1-3]?[0-9]\s*$')
    default_error_messages = {'invalid': _(u'Enter a valid network address.')}

    def __init__(self, *args, **kwargs):
        super(NetworkField, self).__init__(self.NET_RE, *args, **kwargs)

    def clean(self, value):
        value = super(NetworkField, self).clean(value).upper()
        ip, mask = value.split('/')
        parts = []
        for part in ip.split('.'):
            number = int(part)
            if not (0 <= number <= 255):
                raise django.forms.ValidationError(_("Invalid address part."))
            parts.append('%s' % part)
        mask = int(mask)
        if not (0 < mask <= 32):
            raise django.forms.ValidationError(_("Invalid mask part."))

        # TODO(rdopiera) Perhaps we should normalize the IP part for the given
        # mask, by zeroing the bits not covered by the mask? At this point we
        # should probably use an IP address calculating library like ipaddr.

        return '%s/%s' % ('.'.join(parts), mask)
