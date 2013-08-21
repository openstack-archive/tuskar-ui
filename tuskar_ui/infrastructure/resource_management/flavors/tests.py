from django.core.urlresolvers import reverse
from django import http
from mox import IsA

from tuskar_ui import api as tuskar
from tuskar_ui.test import helpers as test


class FlavorsTests(test.BaseAdminViewTests):

    @test.create_stubs({tuskar.Flavor: ('get',)})
    def test_detail_flavor(self):
        flavor = self.tuskar_flavors.first()
        resource_class = self.tuskar_resource_classes.first()

        tuskar.Flavor.get(IsA(http.HttpRequest),
                              resource_class.id,
                              flavor.id).AndReturn(flavor)

        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management'
                      ':resource_classes:flavors:detail',
                      args=[resource_class.id, flavor.id])
        res = self.client.get(url)
        self.assertTemplateUsed(res, "infrastructure/resource_management/"
                                     "flavors/detail.html")

    @test.create_stubs({tuskar.Flavor: ('get',)})
    def test_detail_flavor_exception(self):
        flavor = self.tuskar_flavors.first()
        resource_class = self.tuskar_resource_classes.first()

        tuskar.Flavor.get(IsA(http.HttpRequest),
                              resource_class.id,
                              flavor.id).AndRaise(self.exceptions.tuskar)

        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:'
                      'resource_classes:flavors:detail',
                      args=[resource_class.id, flavor.id])
        res = self.client.get(url)

        self.assertRedirectsNoFollow(
            res, reverse('horizon:infrastructure:resource_management:index'))
