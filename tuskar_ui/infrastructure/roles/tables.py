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

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import tables as nodes_tables


class UpdateRole(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Role")
    url = "horizon:infrastructure:roles:update"
    classes = ("ajax-modal",)
    icon = "pencil"

    def allowed(self, request, datum):
        plan = api.tuskar.Plan.get_the_plan(request)

        if datum.id in [role.id for role in plan.role_list]:
            return True
        return False


class RolesTable(tables.DataTable):

    name = tables.Column('name',
                         link="horizon:infrastructure:roles:detail",
                         verbose_name=_("Role"))
    flavor = tables.Column('flavor',
                           verbose_name=_("Flavor"))
    image = tables.Column('image',
                          verbose_name=_("Image"))

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "roles"
        verbose_name = _("Deployment Roles")
        table_actions = ()
        row_actions = (UpdateRole,)
        template = "horizon/common/_enhanced_data_table.html"


class NodeTable(nodes_tables.ProvisionedNodesTable):

    class Meta(object):
        name = "nodetable"
        verbose_name = _("Nodes")
        hidden_title = False
        table_actions = ()
        row_actions = ()
        template = "horizon/common/_enhanced_data_table.html"
