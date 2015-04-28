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

import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables as horizon_tables
from horizon.utils import memoized
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images.images import views

from tuskar_ui import api as tuskar_api
from tuskar_ui.infrastructure.images import forms
from tuskar_ui.infrastructure.images import tables
import tuskar_ui.infrastructure.views as infrastructure_views
from tuskar_ui.utils import utils

LOG = logging.getLogger(__name__)


class IndexView(infrastructure_views.ItemCountMixin,
                horizon_tables.DataTableView):
    table_class = tables.ImagesTable
    template_name = "infrastructure/images/index.html"

    @memoized.memoized_method
    def get_data(self):
        images = []
        filters = self.get_filters()

        sort_dir = 'desc'
        try:
            images, self._more, self._prev = api.glance.image_list_detailed(
                self.request,
                paginate=False,
                filters=filters,
                sort_dir=sort_dir)
            images = [image for image in images
                      if utils.check_image_type(image,
                                                'overcloud provisioning')]
        except Exception:
            msg = _('Unable to retrieve image list.')
            exceptions.handle(self.request, msg)

        plan = tuskar_api.tuskar.Plan.get_the_plan(self.request)
        for image in images:
            image.role = tuskar_api.tuskar.Role.get_by_image(
                self.request, plan, image)

        return images

    def get_filters(self):
        filters = {'is_public': None}
        filter_field = self.table.get_filter_field()
        filter_string = self.table.get_filter_string()
        filter_action = self.table._meta._filter_action
        if filter_field and filter_string and (
                filter_action.is_api_filter(filter_field)):
            if filter_field in ['size_min', 'size_max']:
                invalid_msg = ('API query is not valid and is ignored: %s=%s'
                               % (filter_field, filter_string))
                try:
                    filter_string = long(float(filter_string) * (1024 ** 2))
                    if filter_string >= 0:
                        filters[filter_field] = filter_string
                    else:
                        LOG.warning(invalid_msg)
                except ValueError:
                    LOG.warning(invalid_msg)
            else:
                filters[filter_field] = filter_string
        return filters


class CreateView(views.CreateView):
    submit_url = "horizon:infrastructure:images:create"
    template_name = 'infrastructure/images/create.html'
    success_url = reverse_lazy("horizon:infrastructure:images:index")
    page_title = _("Create Image")


class UpdateView(views.UpdateView):
    template_name = 'infrastructure/images/update.html'
    form_class = forms.UpdateImageForm
    success_url = reverse_lazy('horizon:infrastructure:images:index')
    submit_url = "horizon:infrastructure:images:update"
    submit_label = _("Update Image")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.glance.image_get(self.request, self.kwargs['image_id'])
        except Exception:
            msg = _('Unable to retrieve image.')
            url = reverse_lazy('horizon:infrastructure:images:index')
            exceptions.handle(self.request, msg, redirect=url)
