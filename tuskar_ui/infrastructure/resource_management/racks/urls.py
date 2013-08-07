# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from django.conf.urls import patterns
from django.conf.urls import url

from tuskar_ui.infrastructure. \
    resource_management.racks.views import CreateView
from tuskar_ui.infrastructure. \
    resource_management.racks.views import DetailEditView
from tuskar_ui.infrastructure. \
    resource_management.racks.views import DetailView
from tuskar_ui.infrastructure. \
    resource_management.racks.views import EditRackStatusView
from tuskar_ui.infrastructure. \
    resource_management.racks.views import EditView
from tuskar_ui.infrastructure. \
    resource_management.racks.views import UploadView
from tuskar_ui.infrastructure. \
    resource_management.racks.views import UsageDataView


RACKS = r'^(?P<rack_id>[^/]+)/%s$'
VIEW_MOD = 'tuskar_ui.infrastructure.resource_management.racks.views'


urlpatterns = patterns(VIEW_MOD,
    url(r'^create/$', CreateView.as_view(), name='create'),
    url(r'^upload/$', UploadView.as_view(), name='upload'),
    url(r'^usage_data$', UsageDataView.as_view(), name='usage_data'),
    url(RACKS % 'edit/', EditView.as_view(), name='edit'),
    url(RACKS % 'detail_edit/', DetailEditView.as_view(), name='detail_edit'),
    url(RACKS % 'edit_status/', EditRackStatusView.as_view(),
                                name='edit_status'),
    url(RACKS % 'detail', DetailView.as_view(), name='detail'),
    url(RACKS % 'top_communicating.json', 'top_communicating',
        name='top_communicating'),
    url(RACKS % 'node_health.json', 'node_health', name='node_health'),
    url(RACKS % 'check_state.json', 'check_state', name='check_state'),
)
