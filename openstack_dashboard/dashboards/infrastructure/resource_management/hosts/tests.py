from django.core.urlresolvers import reverse
from openstack_dashboard.test import helpers as test
from openstack_dashboard import api
from mox import IsA
from django import http


class ResourceViewTests(test.BaseAdminViewTests):
    unracked_page = reverse('horizon:infrastructure:'
                            'resource_management:hosts:unracked')

    @test.create_stubs({api.management.Host: ('list_unracked',), })
    def test_unracked(self):
        unracked_hosts = self.management_racks.list()

        api.management.Host.list_unracked(IsA(http.HttpRequest)) \
            .AndReturn(unracked_hosts)

        self.mox.ReplayAll()

        res = self.client.get(self.unracked_page)

        self.assertTemplateUsed(res,
                      'infrastructure/resource_management/hosts/unracked.html')

        unracked_hosts_table = res.context['unracked_hosts_table'].data

        self.assertItemsEqual(unracked_hosts_table, unracked_hosts)
