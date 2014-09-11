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

from tuskar_ui.infrastructure.images.properties import urls as properties_urls
from tuskar_ui.infrastructure.images import views

urlpatterns = urls.patterns(
    '',
    urls.url(r'^$', views.IndexView.as_view(), name='index'),
    urls.url(r'^create/$', views.CreateView.as_view(), name='create'),
    urls.url(r'^(?P<image_id>[^/]+)/update/$',
             views.UpdateView.as_view(), name='update'),
    urls.url(r'^(?P<image_id>[^/]+)/detail/$',
             views.DetailView.as_view(), name='detail'),
    urls.url(r'^(?P<id>[^/]+)/properties/',
             urls.include(properties_urls, namespace='properties')),
)
