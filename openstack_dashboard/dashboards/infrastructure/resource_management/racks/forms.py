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

    def __init__(self, request, *args, **kwargs):
        super(CreateRack, self).__init__(request, *args, **kwargs)
        resource_class_id_choices = [('', _("Select a Resource Class"))]
        for rc in api.management.resource_class_list(request):
            resource_class_id_choices.append((rc.id, rc.name))
        self.fields['resource_class_id'].choices = resource_class_id_choices

    def handle(self, request, data):
        try:
            rack = api.management.rack_create(request, data['name'],
                                              data['resource_class_id'])
            msg = _('Created rack "%s".') % data['name']
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to create rack."))


class EditRack(CreateRack):
    rack_id = forms.CharField(widget=forms.widgets.HiddenInput)

    def handle(self, request, data):
        try:
            # FIXME: This method needs implementation
            # api.management.rack_edit(request, data['rack_id'],
            #                          data['name'], data['resource_class_id'])
            msg = _('Updated rack "%s".') % data["name"]
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to update rack."))
