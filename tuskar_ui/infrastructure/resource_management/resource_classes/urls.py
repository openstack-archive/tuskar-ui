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

from tuskar_ui.infrastructure.resource_management.flavors\
    import urls as flavor_urls
from tuskar_ui.infrastructure.resource_management.resource_classes import views


RESOURCE_CLASS = r'^(?P<resource_class_id>[^/]+)/%s$'
VIEW_MOD = ('tuskar_ui.infrastructure.resource_management.resource_classes.'
            'views')

urlpatterns = defaults.patterns(
    VIEW_MOD,
    defaults.url(r'^create/$', views.CreateView.as_view(), name='create'),
    defaults.url(r'^(?P<resource_class_id>[^/]+)/$',
                 views.DetailView.as_view(),
                 name='detail'),
    defaults.url(RESOURCE_CLASS % 'update',
                 views.UpdateView.as_view(),
                 name='update'),
    defaults.url(RESOURCE_CLASS % 'detail_action',
                 views.DetailActionView.as_view(),
                 name='detail_action'),
    defaults.url(RESOURCE_CLASS % 'detail_update',
                 views.DetailUpdateView.as_view(),
                 name='detail_update'),
    defaults.url(RESOURCE_CLASS % 'update_racks',
                 views.UpdateRacksView.as_view(),
                 name='update_racks'),
    defaults.url(RESOURCE_CLASS % 'update_flavors',
                 views.UpdateFlavorsView.as_view(),
                 name='update_flavors'),
    defaults.url(RESOURCE_CLASS % 'rack_health.json',
                 'rack_health',
                 name='rack_health'),
    defaults.url(r'^(?P<resource_class_id>[^/]+)/flavors/',
                 defaults.include(flavor_urls, namespace='flavors')),
)
