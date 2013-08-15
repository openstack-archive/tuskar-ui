# vim: tabstop=4 shiftwidth=4 softtabstop=4

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from tuskar_ui import api as tuskar

import base64
import csv
import logging
import StringIO

LOG = logging.getLogger(__name__)


class UploadRack(forms.SelfHandlingForm):
    csv_file = forms.FileField(label=_("Choose CSV File"),
                               help_text=("CSV file with rack definitions"),
                               required=False)
    uploaded_data = forms.CharField(widget=forms.HiddenInput(),
                                    required=False)

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        data = csv_file.read() if csv_file else None

        if 'upload' in self.request.POST:
            if not csv_file:
                raise ValidationError(_('CSV file not set.'))
            else:
                try:
                    CSVRack.from_str(data)
                except Exception:
                    LOG.exception("Failed to parse rack CSV file.")
                    raise ValidationError(_('Failed to parse CSV file.'))
        return data

    def clean_uploaded_data(self):
        data = self.cleaned_data['uploaded_data']
        if 'add_racks' in self.request.POST:
            if not data:
                raise ValidationError(_('Upload CSV file first'))
        elif 'upload' in self.request.POST:
            # reset obsolete uploaded data
            self.data['uploaded_data'] = None
        return data

    def handle(self, request, data):
        if 'upload' in self.request.POST:
            # if upload button was pressed, stay on the same page
            # but show content of the CSV file in table
            racks_str = self.cleaned_data['csv_file']
            self.initial['racks'] = CSVRack.from_str(racks_str)
            self.data['uploaded_data'] = base64.b64encode(racks_str)
            return False
        else:
            fails = []
            successes = []
            racks_str = self.cleaned_data['uploaded_data']
            racks = CSVRack.from_str(base64.b64decode(racks_str))
            # get the resource class ids by resource class names
            rclass_ids = dict((rc.name, rc.id) for rc in
                    tuskar.ResourceClass.list(request))
            for rack in racks:
                try:
                    tuskar.Rack.create(request, name=rack.name,
                                           resource_class_id=
                                               rclass_ids[rack.resource_class],
                                           location=rack.region,
                                           subnet=rack.subnet)
                    # FIXME: will have to handle nodes once proper attributes
                    # for nodes are added
                    successes.append(rack.name)
                except:
                    LOG.exception("Exception in processing rack CSV file.")
                    fails.append(rack.name)
            if successes:
                messages.success(request,
                                 _('Added %d racks.') % len(successes))
            if fails:
                messages.error(request,
                               _('Failed to add following racks: %s') %
                                   (',').join(fails))
            return True


class CSVRack:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.resource_class = kwargs['resource_class']
        self.region = kwargs['region']
        self.subnet = kwargs['subnet']
        self.nodes = kwargs['nodes']

    @classmethod
    def from_str(cls, csv_str):
        racks = []
        csvreader = csv.reader(StringIO.StringIO(csv_str), delimiter=',')
        for row in csvreader:
            # ignore empty rows
            if not row:
                continue
            racks.append(cls(id=row[0],
                             name=row[0],
                             resource_class=row[1],
                             subnet=row[2],
                             region=row[3],
                             nodes=row[4].split()))
        return racks

    def nodes_count(self):
        return len(self.nodes)


class UpdateRackStatus(forms.SelfHandlingForm):

    def handle(self, request, data):
        try:
            rack = self.initial.get('rack', None)
            action = request.GET.get('action')

            if action == "provision":
                tuskar.Rack.provision(
                    request,
                    rack.id)

                msg = _('Rack "%s" is being provisioned.') % rack.name
            else:
                if action == "start":
                    rack.state = "active"
                elif action == "unprovision":
                    rack.state = "unprovisioned"
                elif action == "reboot":
                    rack.state = "active"
                elif action == "shutdown":
                    rack.state = "off"

                rack = tuskar.Rack.update(
                    request,
                    rack.id,
                    {'state': rack.state}
                )

                msg = _('Updated rack "%s" status.') % rack.name
            messages.success(request, msg)
            return True
        except:
            exceptions.handle(request, _("Unable to update Rack status."))
