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

from django.conf.urls import defaults

from tuskar_ui.infrastructure.resource_management.flavor_templates import views


FLAVOR_TEMPLATES = r'^(?P<flavor_template_id>[^/]+)/%s$'
VIEW_MOD = 'tuskar_ui.infrastructure.' \
           'resource_management.flavor_templates.views'

urlpatterns = defaults.patterns(VIEW_MOD,
    defaults.url(r'^create/$', views.CreateView.as_view(), name='create'),
    defaults.url(FLAVOR_TEMPLATES % 'edit/$',
                 views.EditView.as_view(),
                 name='edit'),
    defaults.url(FLAVOR_TEMPLATES % 'detail_edit/$',
                 views.DetailEditView.as_view(),
                 name='detail_edit'),
    defaults.url(FLAVOR_TEMPLATES % 'detail',
                 views.DetailView.as_view(),
                 name='detail'),
    defaults.url(FLAVOR_TEMPLATES % 'active_instances_data',
                 views.ActiveInstancesDataView.as_view(),
                 name='active_instances_data')
)
