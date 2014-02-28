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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import views
from horizon import workflows

from tuskar_ui import api
from tuskar_ui.infrastructure.node_profiles \
    import tables as node_profiles_tables
from tuskar_ui.infrastructure.node_profiles \
    import workflows as node_profiles_workflows


class IndexView(tables.DataTableView):
    table_class = node_profiles_tables.NodeProfilesTable
    template_name = 'infrastructure/node_profiles/index.html'

    def get_data(self):
        try:
            node_profiles = api.NodeProfile.list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve node profile list.'))
            return []
        node_profiles.sort(key=lambda np: (np.vcpus, np.ram, np.disk))
        return node_profiles


class CreateView(workflows.WorkflowView):
    workflow_class = node_profiles_workflows.CreateNodeProfile
    template_name = 'infrastructure/node_profiles/create.html'


class DetailView(views.APIView):
    template_name = 'infrastructure/node_profiles/details.html'

    def get_data(self, request, context, *args, **kwargs):
        flavor_id = kwargs.get('flavor_id')
        try:
            node_profile = api.NodeProfile.get(request, flavor_id)
        except Exception:
            node_profile = None
            redirect = 'horizon:infrastructure:node_profiles:index'
            msg = _('Unable to retrieve node profile with ID "%s"') % flavor_id
            exceptions.handle(request, msg, redirect=reverse_lazy(redirect))

        context['node_profile'] = node_profile
        return context
