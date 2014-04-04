# -*- coding: utf8 -*-
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

from django.conf import urls

from tuskar_ui.infrastructure.overcloud import views


urlpatterns = urls.patterns(
    '',
    urls.url(r'^$', views.IndexView.as_view(), name='index'),
    urls.url(r'^create/$', views.CreateView.as_view(), name='create'),
    urls.url(r'^(?P<overcloud_id>[^/]+)/undeploy-in-progress$',
             views.UndeployInProgressView.as_view(),
             name='undeploy_in_progress'),
    urls.url(r'^create/role-edit/(?P<role_id>[^/]+)$',
             views.OvercloudRoleEdit.as_view(), name='role_edit'),
    urls.url(r'^(?P<overcloud_id>[^/]+)/$', views.DetailView.as_view(),
             name='detail'),
    urls.url(r'^(?P<overcloud_id>[^/]+)/scale$', views.Scale.as_view(),
             name='scale'),
    urls.url(r'^(?P<overcloud_id>[^/]+)/role/(?P<role_id>[^/]+)$',
             views.OvercloudRoleView.as_view(), name='role'),
    urls.url(r'^(?P<overcloud_id>[^/]+)/undeploy-confirmation$',
             views.UndeployConfirmationView.as_view(),
             name='undeploy_confirmation'),

)
