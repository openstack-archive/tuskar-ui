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

from django.conf import urls

from tuskar_ui.infrastructure.resource_management.racks import views

RACKS = r'^(?P<rack_id>[^/]+)/%s$'
VIEW_MOD = 'tuskar_ui.infrastructure.resource_management.racks.views'


urlpatterns = urls.patterns(
    VIEW_MOD,
    urls.url(r'^create/$', views.CreateView.as_view(), name='create'),
    urls.url(r'^upload/$', views.UploadView.as_view(), name='upload'),
    urls.url(r'^usage_data$',
             views.UsageDataView.as_view(),
             name='usage_data'),
    urls.url(RACKS % 'edit/', views.EditView.as_view(), name='edit'),
    urls.url(RACKS % 'detail_edit/',
             views.DetailEditView.as_view(),
             name='detail_edit'),
    urls.url(RACKS % 'edit_status/',
             views.EditRackStatusView.as_view(),
             name='edit_status'),
    urls.url(RACKS % 'detail', views.DetailView.as_view(), name='detail'),
    urls.url(RACKS % 'top_communicating.json',
             'top_communicating',
             name='top_communicating'),
    urls.url(RACKS % 'node_health.json', 'node_health', name='node_health'),
    urls.url(RACKS % 'check_state.json', 'check_state', name='check_state'),
)
