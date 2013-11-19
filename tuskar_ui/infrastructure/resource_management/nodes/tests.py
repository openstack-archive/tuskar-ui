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

from django.core import urlresolvers
from django import http

import mox

from tuskar_ui import api as tuskar
from tuskar_ui.test import helpers as test


class NodeViewTests(test.BaseAdminViewTests):
    unracked_page = urlresolvers.reverse(
        'horizon:infrastructure:resource_management:nodes:unracked')

    @test.create_stubs({tuskar.BaremetalNode: ('list_unracked',), })
    def test_unracked(self):
        unracked_baremetal_nodes = self.baremetal_unracked_nodes.list()

        tuskar.BaremetalNode.list_unracked(
            mox.IsA(http.HttpRequest)).AndReturn(unracked_baremetal_nodes)
        self.mox.ReplayAll()

        res = self.client.get(self.unracked_page)
        self.assertTemplateUsed(
            res,
            'infrastructure/resource_management/nodes/unracked.html')

        unracked_nodes_table = res.context['unracked_nodes_table'].data
        self.assertItemsEqual(unracked_nodes_table, unracked_baremetal_nodes)

    @test.create_stubs({
        tuskar.BaremetalNode: ('get',),
        tuskar.TuskarNode: ('list', 'running_virtual_machines',
                            'list_flavors'),
        tuskar.Rack: ('get',),
    })
    def test_detail_node(self):
        baremetal_node = self.baremetal_nodes.first()
        tuskar_nodes = self.tuskar_nodes.list()
        rack = self.tuskar_racks.first()

        tuskar.BaremetalNode.get(mox.IsA(http.HttpRequest),
                                 baremetal_node.id).AndReturn(baremetal_node)
        tuskar.TuskarNode.list(None).AndReturn(tuskar_nodes)
        tuskar.Rack.get(None, rack.id).AndReturn(rack)
        tuskar.BaremetalNode.get(None,
                                 baremetal_node.id).AndReturn(baremetal_node)
        self.mox.ReplayAll()

        tuskar.TuskarNode.running_virtual_machines = []
        tuskar.TuskarNode.list_flavors = []

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:nodes:detail',
            args=[baremetal_node.id])
        res = self.client.get(url)
        self.assertTemplateUsed(
            res, 'infrastructure/resource_management/nodes/detail.html')

    @test.create_stubs({tuskar.BaremetalNode: ('get',)})
    def test_detail_node_exception(self):
        baremetal_node = self.baremetal_nodes.first()

        tuskar.BaremetalNode.get(
            mox.IsA(http.HttpRequest),
            baremetal_node.id).AndRaise(self.exceptions.tuskar)

        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:nodes:detail',
            args=[baremetal_node.id])
        res = self.client.get(url)

        self.assertRedirectsNoFollow(
            res,
            urlresolvers.reverse(
                'horizon:infrastructure:resource_management:index'))
