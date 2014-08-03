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

from horizon import views as horizon_views

from tuskar_ui import api


class IndexView(horizon_views.APIView):
    template_name = 'infrastructure/parameters/index.html'

    def get_data(self, request, context, *args, **kwargs):
        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        context['plan'] = plan
        context['roles'] = plan.role_list
        return context
