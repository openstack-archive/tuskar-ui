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

from django.utils.translation import ugettext_lazy as _
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images.images import (
    tables as project_tables)


class DeleteImage(project_tables.DeleteImage):
    def allowed(self, request, image=None):
        if image and image.protected:
            return False
        else:
            return True


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, image_id):
        image = api.glance.image_get(request, image_id)
        return image


class ImageFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (('name', _("Image Name ="), True),
                      ('status', _('Status ='), True),
                      ('disk_format', _('Format ='), True),
                      ('size_min', _('Min. Size (MB)'), True),
                      ('size_max', _('Max. Size (MB)'), True))


class EditImage(project_tables.EditImage):
    url = "horizon:infrastructure:images:update"

    def allowed(self, request, image=None):
        return True


class ImagesTable(tables.DataTable):

    name = tables.Column('name',
                         verbose_name=_("Image Name"))
    disk_format = tables.Column('disk_format',
                                verbose_name=_("Format"))
    role = tables.Column(lambda image:
                         image.role.name if image.role else '-',
                         verbose_name=_("Deployment Role"))

    class Meta:
        name = "images"
        row_class = UpdateRow
        verbose_name = _("Provisioning Images")
        table_actions = (DeleteImage,
                         ImageFilterAction)
        row_actions = (EditImage, DeleteImage)
