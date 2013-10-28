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

from django import conf
from django.conf.urls import defaults

from tuskar_ui.infrastructure.resource_management.nodes\
    import urls as node_urls
from tuskar_ui.infrastructure.resource_management.racks\
    import urls as rack_urls
from tuskar_ui.infrastructure.resource_management.resource_classes\
    import urls as resource_classes_urls
from tuskar_ui.infrastructure.resource_management import views
from tuskar_ui.test import urls as test_urls


urlpatterns = defaults.patterns(
    '',
    defaults.url(r'^$', views.IndexView.as_view(), name='index'),
    defaults.url(r'^provision$', views.ProvisionView.as_view(),
                 name='provision'),
    defaults.url(r'^provisioning_state.json$', views.provisioning_state,
                 name='provisioning_state'),
    defaults.url(r'^racks/', defaults.include(rack_urls, namespace='racks')),
    defaults.url(r'^resource_classes/',
                 defaults.include(resource_classes_urls,
                                  namespace='resource_classes')),
    defaults.url(r'^nodes/', defaults.include(node_urls, namespace='nodes')),
)

if conf.settings.DEBUG:
    urlpatterns += defaults.patterns(
        '', defaults.url(r'^qunit$',
                         defaults.include(test_urls, namespace='tests')))
