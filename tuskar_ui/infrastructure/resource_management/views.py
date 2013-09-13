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

"""
Views for Resource Management.
"""

from django.core import urlresolvers
from django import http
from django.utils import simplejson

from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management import forms
from tuskar_ui.infrastructure.resource_management import tabs


class IndexView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.ResourceManagementTabs
    template_name = 'infrastructure/resource_management/index.html'


class ProvisionView(tabs.ProvisioningInfoMixin, horizon_forms.ModalFormView):
    form_class = forms.Provision
    template_name = 'infrastructure/resource_management/provision.html'

    def get_success_url(self):
        # Redirect to previous URL
        default_url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:index')
        return self.request.META.get('HTTP_REFERER', default_url)


def provisioning_state(request, rack_id=None):
    racks = tuskar.Rack.list(request)
    (unprovisioned_racks, provisioning_racks,
        state) = tabs.get_provision_racks_and_state(racks)
    return http.HttpResponse(simplejson.dumps({'state': state}),
                             mimetype="application/json")
