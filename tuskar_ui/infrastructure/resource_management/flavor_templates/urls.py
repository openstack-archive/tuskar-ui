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

from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from tuskar_ui.infrastructure.resource_management.flavor_templates.views \
    import ActiveInstancesDataView
from tuskar_ui.infrastructure.resource_management.flavor_templates.views \
    import CreateView
from tuskar_ui.infrastructure.resource_management.flavor_templates.views \
    import DetailEditView
from tuskar_ui.infrastructure.resource_management.flavor_templates.views \
    import DetailView
from tuskar_ui.infrastructure.resource_management.flavor_templates.views \
    import EditView


FLAVOR_TEMPLATES = r'^(?P<flavor_template_id>[^/]+)/%s$'
VIEW_MOD = 'tuskar_ui.infrastructure.' \
           'resource_management.flavor_templates.views'

urlpatterns = patterns(VIEW_MOD,
    url(r'^create/$', CreateView.as_view(), name='create'),
    url(FLAVOR_TEMPLATES % 'edit/$', EditView.as_view(), name='edit'),
    url(FLAVOR_TEMPLATES % 'detail_edit/$',
        DetailEditView.as_view(), name='detail_edit'),
    url(FLAVOR_TEMPLATES % 'detail', DetailView.as_view(), name='detail'),
    url(FLAVOR_TEMPLATES % 'active_instances_data',
        ActiveInstancesDataView.as_view(), name='active_instances_data')
)
