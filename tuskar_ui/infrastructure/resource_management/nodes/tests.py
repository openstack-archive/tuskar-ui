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

from django.core.urlresolvers import reverse
from django import http

from mox import IsA

from tuskar_ui import api as tuskar
from tuskar_ui.test import helpers as test


class ResourceViewTests(test.BaseAdminViewTests):
    unracked_page = reverse('horizon:infrastructure:'
                            'resource_management:nodes:unracked')

    @test.create_stubs({tuskar.Node: ('list_unracked',), })
    def test_unracked(self):
        unracked_nodes = self.baremetal_unracked_nodes.list()

        tuskar.Node.list_unracked(IsA(http.HttpRequest)) \
            .AndReturn(unracked_nodes)

        self.mox.ReplayAll()

        res = self.client.get(self.unracked_page)

        self.assertTemplateUsed(res,
                      'infrastructure/resource_management/nodes/unracked.html')

        unracked_nodes_table = res.context['unracked_nodes_table'].data

        self.assertItemsEqual(unracked_nodes_table, unracked_nodes)
