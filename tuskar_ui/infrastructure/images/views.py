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

from horizon import tables as horizon_tables

from openstack_dashboard.api import glance

from tuskar_ui import api
from tuskar_ui.infrastructure.images import tables


class IndexView(horizon_tables.DataTableView):
    table_class = tables.ImagesTable
    template_name = "infrastructure/images/index.html"

    def get_data(self):
        plan = api.tuskar.OvercloudPlan.get_the_plan(self.request)
        images = glance.image_list_detailed(self.request)[0]
        # TODO(tzumainn): re-architect a bit to avoid inefficiency
        for image in images:
            image.role = api.tuskar.OvercloudRole.get_by_image(
                self.request, plan, image)
        return images
