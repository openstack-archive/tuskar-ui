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

from openstack_dashboard.dashboards.admin.flavors \
    import views as flavor_views

from tuskar_ui.infrastructure.profiles import tables
from tuskar_ui.infrastructure.profiles import workflows


class IndexView(flavor_views.IndexView):
    table_class = tables.ProfilesTable
    template_name = 'infrastructure/profiles/index.html'


class CreateView(flavor_views.CreateView):
    workflow_class = workflows.CreateProfile
    template_name = 'infrastructure/profiles/create.html'


class UpdateView(flavor_views.UpdateView):
    workflow_class = workflows.UpdateProfile
    template_name = 'infrastructure/profiles/update.html'
