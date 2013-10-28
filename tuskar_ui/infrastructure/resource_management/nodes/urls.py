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

from django.conf.urls import defaults

from tuskar_ui.infrastructure.resource_management.nodes import views


NODES = r'^(?P<node_id>[^/]+)/%s$'
VIEW_MOD = 'tuskar_ui.infrastructure.resource_management.nodes.views'


urlpatterns = defaults.patterns(
    VIEW_MOD,
    defaults.url(NODES % 'detail', views.DetailView.as_view(), name='detail'),
    defaults.url(r'^unracked/$',
                 views.UnrackedView.as_view(),
                 name='unracked'),
)
