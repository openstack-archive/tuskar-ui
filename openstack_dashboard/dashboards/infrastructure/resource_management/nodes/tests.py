from django.core.urlresolvers import reverse
from openstack_dashboard.test import helpers as test
from openstack_dashboard import api
from mox import IsA
from django import http


class ResourceViewTests(test.BaseAdminViewTests):
    unracked_page = reverse('horizon:infrastructure:'
                            'resource_management:nodes:unracked')

    @test.create_stubs({api.tuskar.Node: ('list_unracked',), })
    def test_unracked(self):
        unracked_nodes = self.tuskar_racks.list()

        api.tuskar.Node.list_unracked(IsA(http.HttpRequest)) \
            .AndReturn(unracked_nodes)

        self.mox.ReplayAll()

        res = self.client.get(self.unracked_page)

        self.assertTemplateUsed(res,
                      'infrastructure/resource_management/nodes/unracked.html')

        unracked_nodes_table = res.context['unracked_nodes_table'].data

        self.assertItemsEqual(unracked_nodes_table, unracked_nodes)
