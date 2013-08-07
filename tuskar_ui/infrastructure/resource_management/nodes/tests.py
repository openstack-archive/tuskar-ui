from django.core.urlresolvers import reverse
from django import http

from mox import IsA

from tuskar_ui import api as tuskar
from openstack_dashboard.test import helpers as test


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
