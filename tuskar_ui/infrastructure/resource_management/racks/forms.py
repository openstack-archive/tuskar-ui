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

import django.forms
from django.utils.translation import ugettext_lazy as _  # noqa

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
                raise django.forms.ValidationError(_('CSV file not set.'))
            else:
                try:
                    CSVRack.from_str(data)
                except Exception:
                    LOG.exception("Failed to parse rack CSV file.")
                    raise django.forms.ValidationError(
                        _('Failed to parse CSV file.'))
        return data

    def clean_uploaded_data(self):
        data = self.cleaned_data['uploaded_data']
        if 'add_racks' in self.request.POST:
            if not data:
                raise django.forms.ValidationError(_('Upload CSV file first'))
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
                    tuskar.Rack.create(
                        request,
                        name=rack.name,
                        resource_class_id=rclass_ids[rack.resource_class],
                        location=rack.region,
                        subnet=rack.subnet,
                    )
                    # FIXME: will have to handle nodes once proper attributes
                    # for nodes are added
                    successes.append(rack.name)
                except Exception:
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
            rack.state = {
                'start': 'active',
                'unprovision': 'unprovisioned',
                'reboot': 'active',
                'shutdown': 'off',
            }[action]
            rack = tuskar.Rack.update(request, rack.id, {'state': rack.state})
        except Exception:
            exceptions.handle(request, _("Unable to update Rack status."))
        else:
            msg = _('Updated rack "%s" status.') % rack.name
            messages.success(request, msg)
            return True
