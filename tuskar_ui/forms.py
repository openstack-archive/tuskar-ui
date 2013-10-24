from django import forms
from django.utils.translation import ugettext_lazy as _  # noqa
import netaddr


class NumberInput(forms.widgets.TextInput):
    input_type = 'number'


class NetworkField(forms.fields.Field):
    def clean(self, value):
        try:
            return str(netaddr.IPNetwork(value, version=4))
        except netaddr.AddrFormatError:
            raise forms.ValidationError(_("Enter valid IPv4 network address."))
