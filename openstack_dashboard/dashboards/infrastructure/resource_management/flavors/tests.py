from django import http
from django.core.urlresolvers import reverse
from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


class FlavorsTests(test.BaseAdminViewTests):

    @test.create_stubs({api.management: ('flavor_list', 'flavor_create'), })
    def test_create_flavor(self):
        flavor = self.flavors.first()

        api.management.flavor_list(IsA(http.HttpRequest))
        api.management.flavor_create(IsA(http.HttpRequest),
                                     flavor.name).AndReturn(flavor)
        self.mox.ReplayAll()

        url = reverse(
            'horizon:infrastructure:resource_management:flavors:create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            resp, "infrastructure/resource_management/flavors/create.html")

        data = {'name': flavor.name}
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(
            resp, reverse('horizon:infrastructure:resource_management:index'))

    @test.create_stubs({api.management: ('flavor_list',
                                         'flavor_update',
                                         'flavor_get'), })
    def test_edit_flavor(self):
        flavor = self.flavors.first()  # has no extra spec

        # GET
        api.management.flavor_get(IsA(http.HttpRequest),
                                  flavor.id).AndReturn(flavor)

        # POST
        api.management.flavor_list(IsA(http.HttpRequest))
        api.management.flavor_update(IsA(http.HttpRequest),
                                     flavor.id,
                                     flavor.name).AndReturn(flavor)
        api.management.flavor_get(IsA(http.HttpRequest),
                                  flavor.id).AndReturn(flavor)
        self.mox.ReplayAll()

        # get_test
        url = reverse(
            'horizon:infrastructure:resource_management:flavors:edit',
            args=[flavor.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            resp, "infrastructure/resource_management/flavors/edit.html")

        # post test
        data = {'flavor_id': flavor.id,
                'name': flavor.name}
        resp = self.client.post(url, data)
        self.assertNoFormErrors(resp)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(
            resp, reverse('horizon:infrastructure:resource_management:index'))

    @test.create_stubs({api.management: ('flavor_list',
                                         'flavor_delete'), })
    def test_delete_flavor(self):
        flavor = self.flavors.first()

        api.management.flavor_list(IsA(http.HttpRequest)).\
            AndReturn(self.flavors.list())
        api.management.flavor_delete(IsA(http.HttpRequest), flavor.id)
        self.mox.ReplayAll()

        form_data = {'action': 'flavors__delete__%s' % flavor.id}
        res = self.client.post(
            reverse('horizon:infrastructure:resource_management:index'),
            form_data)

        self.assertRedirectsNoFollow(
            res, reverse('horizon:infrastructure:resource_management:index'))
