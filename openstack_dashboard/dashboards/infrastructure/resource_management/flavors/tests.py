from django import http
from django.core.urlresolvers import reverse
from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


class FlavorsTests(test.BaseAdminViewTests):

    @test.create_stubs({api.tuskar.Flavor: ('list', 'create')})
    def test_create_flavor(self):
        flavor = self.tuskar_flavors.first()

        api.tuskar.Flavor.list(
            IsA(http.HttpRequest)).AndReturn([])
        api.tuskar.Flavor.create(IsA(http.HttpRequest),
                                     flavor.name,
                                     0, 0, 0, 0, 0).AndReturn(flavor)
        self.mox.ReplayAll()

        url = reverse(
            'horizon:infrastructure:resource_management:flavors:create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            resp, "infrastructure/resource_management/flavors/create.html")

        data = {'name': flavor.name,
                'vcpu': 0,
                'ram': 0,
                'root_disk': 0,
                'ephemeral_disk': 0,
                'swap_disk': 0}
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(
            resp, reverse('horizon:infrastructure:resource_management:index'))

    @test.create_stubs({api.tuskar.Flavor: ('list', 'update', 'get')})
    def test_edit_flavor_get(self):
        flavor = self.tuskar_flavors.first()  # has no extra spec

        api.tuskar.Flavor.get(IsA(http.HttpRequest),
                                  flavor.id).AndReturn(flavor)
        self.mox.ReplayAll()

        url = reverse(
            'horizon:infrastructure:resource_management:flavors:edit',
            args=[flavor.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            resp, "infrastructure/resource_management/flavors/edit.html")

    @test.create_stubs({api.tuskar.Flavor: ('list', 'update', 'get')})
    def test_edit_flavor_post(self):
        flavor = self.tuskar_flavors.first()  # has no extra spec

        api.tuskar.Flavor.list(
            IsA(http.HttpRequest)).AndReturn(self.tuskar_flavors.list())
        api.tuskar.Flavor.update(IsA(http.HttpRequest),
                                     flavor.id,
                                     flavor.name,
                                     0, 0, 0, 0, 0).AndReturn(flavor)
        api.tuskar.Flavor.get(IsA(http.HttpRequest),
                                  flavor.id).AndReturn(flavor)
        self.mox.ReplayAll()

        data = {'flavor_id': flavor.id,
                'name': flavor.name,
                'vcpu': 0,
                'ram': 0,
                'root_disk': 0,
                'ephemeral_disk': 0,
                'swap_disk': 0}
        url = reverse(
            'horizon:infrastructure:resource_management:flavors:edit',
            args=[flavor.id])
        resp = self.client.post(url, data)
        self.assertNoFormErrors(resp)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(
            resp, reverse('horizon:infrastructure:resource_management:index'))

    @test.create_stubs({api.tuskar.Flavor: ('list', 'delete')})
    def test_delete_flavor(self):
        flavor = self.tuskar_flavors.first()

        api.tuskar.Flavor.list(IsA(http.HttpRequest)).\
            AndReturn(self.tuskar_flavors.list())
        api.tuskar.Flavor.delete(IsA(http.HttpRequest), flavor.id)
        self.mox.ReplayAll()

        form_data = {'action': 'flavors__delete__%s' % flavor.id}
        res = self.client.post(
            reverse('horizon:infrastructure:resource_management:index'),
            form_data)

        self.assertRedirectsNoFollow(
            res, reverse('horizon:infrastructure:resource_management:index'))

    @test.create_stubs({api.tuskar.Flavor: ('get',)})
    def test_detail_flavor(self):
        flavor = self.tuskar_flavors.first()

        api.tuskar.Flavor.get(IsA(http.HttpRequest),
                                  flavor.id).AndReturn(flavor)
        api.tuskar.Flavor.resource_classes = self. \
            tuskar_resource_classes

        self.mox.ReplayAll()

        url = reverse(
            'horizon:infrastructure:resource_management:flavors:detail',
            args=[flavor.id])
        res = self.client.get(url)
        self.assertTemplateUsed(
            res, "infrastructure/resource_management/flavors/detail.html")
