from collections import namedtuple

from django import http
from django.core.urlresolvers import reverse
from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test
#from novaclient.v1_1 import flavors


class FlavorsTests(test.BaseAdminViewTests):

    #@test.create_stubs({api.management: ('flavor_list', 'flavor_create'), })
    def test_create_flavor(self):
        #flavor = self.flavors.first()
        Flavor = namedtuple('Flavor', 'id, name')
        flavor = Flavor('1', 'test')

        #api.management.flavor_create(IsA(http.HttpRequest),
        #                             flavor.name).AndReturn(flavor)
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

    # keeping the 2 edit tests separate to aid debug breaks
    #@test.create_stubs({api.management: ('flavor_list',
    #                               'flavor_create',
    #                               'flavor_delete',
    #                               'flavor_get'), })
    def test_edit_flavor(self):
        #flavor = self.flavors.first()  # has no extra spec
        Flavor = namedtuple('Flavor', 'id, name')
        flavor = Flavor('1', 'test')

        #new_flavor = flavors.Flavor(flavors.FlavorManager(None),
        #                            {'id':
        #                             "cccccccc-cccc-cccc-cccc-cccccccccccc",
        #                             'name': flavor.name})
        # GET
        #api.management.flavor_get(
        #    IsA(http.HttpRequest), flavor.id).AndReturn(flavor)

        # POST
        #api.management.flavor_list(IsA(http.HttpRequest))
        #api.management.flavor_get(
        #    IsA(http.HttpRequest), flavor.id).AndReturn(flavor)
        #api.management.flavor_delete(IsA(http.HttpRequest), flavor.id)
        #api.management.flavor_create(IsA(http.HttpRequest),
        #                       new_flavor.name).AndReturn(new_flavor)
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

    #@test.create_stubs({api.management: ('flavor_delete'), })
    def test_delete_flavor(self):
        #flavor = self.flavors.first()
        Flavor = namedtuple('Flavor', 'id, name')
        flavor = Flavor('1', 'test')

        #api.management.flavor_delete(IsA(http.HttpRequest), flavor.id)

        self.mox.ReplayAll()

        form_data = {'action': 'flavors__delete__%s' % flavor.id}
        res = self.client.post(
            reverse('horizon:infrastructure:resource_management:index'),
            form_data)

        self.assertRedirectsNoFollow(
            res, reverse('horizon:infrastructure:resource_management:index'))
