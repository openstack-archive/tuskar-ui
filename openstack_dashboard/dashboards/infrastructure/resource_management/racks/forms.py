# vim: tabstop=4 shiftwidth=4 softtabstop=4

import re

from django.core import validators
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api


class CreateRack(forms.SelfHandlingForm):
    name = forms.RegexField(label=_("Name"),
                            max_length=25,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _('Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')})
    resource_class_id = forms.ChoiceField(label=_("Resource Class"))
    location = forms.CharField(label=_("Location"))
    subnet = forms.CharField(label=_("IP Subnet"))

    def clean(self):
        cleaned_data = super(CreateRack, self).clean()
        name = cleaned_data.get('name')
        rack_id = self.initial.get('rack_id', None)
        resource_class_id = cleaned_data.get('resource_class_id')
        location = cleaned_data.get('location')
        subnet = cleaned_data.get('subnet')
        try:
            racks = api.management.Rack.list(self.request)
        except:
            racks = []
            exceptions.check_message(['Connection', 'refused'],
                _("Unable to retrieve rack list."))
            raise

        # Validations: detect duplicates
        for rack in racks:
            other_record = rack_id != rack.id
            if rack.name == name and other_record:
                raise forms.ValidationError(
                    _('The name %s is already used by another rack.')
                    % name)
            if rack.subnet == subnet and other_record:
                raise forms.ValidationError(
                    _('The subnet %s is already assigned to rack %s.')
                    % (subnet, rack.name))

        return cleaned_data

    def __init__(self, request, *args, **kwargs):
        super(CreateRack, self).__init__(request, *args, **kwargs)
        resource_class_id_choices = [('', _("Select a Resource Class"))]
        for rc in api.management.ResourceClass.list(request):
            resource_class_id_choices.append((rc.id, rc.name))
        self.fields['resource_class_id'].choices = resource_class_id_choices

    def handle(self, request, data):
        try:
            rack = api.management.Rack.create(request, data['name'],
                                              data['resource_class_id'],
                                              data['location'],
                                              data['subnet'])
            msg = _('Created rack "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to create rack."))


class EditRack(CreateRack):
    rack_id = forms.CharField(widget=forms.widgets.HiddenInput)

    def handle(self, request, data):
        try:
            api.management.Rack.update(request, data['rack_id'],
                                     name=data['name'],
                                     subnet=data['subnet'],
                                     resource_class_id=
                                        data['resource_class_id'],
                                     location=data['location'])
            msg = _('Updated rack "%s".') % data["name"]
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to update rack."))
