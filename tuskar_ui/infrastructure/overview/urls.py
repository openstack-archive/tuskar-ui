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

from tuskar_ui.infrastructure.overview import views


urlpatterns = urls.patterns(
    '',
    urls.url(r'^$', views.IndexView.as_view(), name='index'),
    urls.url(r'^deploy-confirmation$',
             views.DeployConfirmationView.as_view(),
             name='deploy_confirmation'),
    urls.url(r'^undeploy-confirmation$',
             views.UndeployConfirmationView.as_view(),
             name='undeploy_confirmation'),
    urls.url(r'^post-deploy-init$',
             views.PostDeployInitView.as_view(),
             name='post_deploy_init'),
    urls.url(r'^scale-out$',
             views.ScaleOutView.as_view(),
             name='scale_out'),
)
