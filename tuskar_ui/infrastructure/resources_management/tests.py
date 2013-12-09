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

from django.core.urlresolvers import reverse
from django import http

from mox import IsA  # noqa

from tuskar_ui import api as tuskar
from tuskar_ui.test import helpers as test

INDEX_URL = reverse('horizon:infrastructure:resources_management:index')


class ManagementNodesTests(test.BaseAdminViewTests):
    def setUp(self):
        super(ManagementNodesTests, self).setUp()

    @test.create_stubs({
        tuskar.BaremetalNode: ('list',),
    })
    def test_index(self):
        management_nodes = self.baremetal_nodes.list()

        tuskar.BaremetalNode.list(IsA(http.HttpRequest)).AndReturn(management_nodes)
        self.mox.ReplayAll()

        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/resources_management/index.html')

        self.assertItemsEqual(res.context['management_nodes_table'].data,
                              management_nodes)
