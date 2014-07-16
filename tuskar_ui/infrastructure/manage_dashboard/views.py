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

from django.views import generic
from tuskar_ui import api


class IndexView(generic.TemplateView):
    template_name = 'infrastructure/manage_dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if api.node.Node.list(self.request):
            context['register_nodes'] = 'done'
        else:
            context['register_nodes'] = 'todo'

        if api.flavor.Flavor.list(self.request):
            context['create_flavors'] = 'done'
        else:
            context['create_flavors'] = 'todo'

        # Deployment roles are static in this iteration
        context['create_deployment_roles'] = 'done'

        # XXX add test for plans.
        context['create_deployment_plan'] = 'todo'

        return context
