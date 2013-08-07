# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
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

from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from tuskar_ui.infrastructure. \
    resource_management.flavors import urls as flavor_urls
from tuskar_ui.infrastructure. \
    resource_management.nodes import urls as node_urls
from tuskar_ui.infrastructure. \
    resource_management.racks import urls as rack_urls
from tuskar_ui.infrastructure. \
    resource_management.resource_classes import urls as resource_classes_urls
from tuskar_ui.infrastructure. \
    resource_management.views import IndexView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'flavors/', include(flavor_urls, namespace='flavors')),
    url(r'racks/', include(rack_urls, namespace='racks')),
    url(r'resource_classes/',
        include(resource_classes_urls, namespace='resource_classes')),
    url(r'nodes/', include(node_urls, namespace='nodes')),
)
