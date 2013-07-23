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

from django.conf.urls.defaults import patterns, url, include

from .views import (CreateView, UpdateView, DetailView, UpdateRacksView,
                    UpdateFlavorsView)

RESOURCE_CLASS = r'^(?P<resource_class_id>[^/]+)/%s$'
VIEW_MOD = 'openstack_dashboard.dashboards.infrastructure.' \
           'resource_management.resource_classes.views'

urlpatterns = patterns(
    VIEW_MOD,
    url(r'^create$', CreateView.as_view(), name='create'),
    url(r'^(?P<resource_class_id>[^/]+)/$',
        DetailView.as_view(), name='detail'),
    url(RESOURCE_CLASS % 'update', UpdateView.as_view(), name='update'),
    url(RESOURCE_CLASS % 'update_racks', UpdateRacksView.as_view(),
        name='update_racks'),
    url(RESOURCE_CLASS % 'update_flavors', UpdateFlavorsView.as_view(),
        name='update_flavors'),
    url(RESOURCE_CLASS % 'rack_health.json', 'rack_health',
        name='rack_health'),
)
