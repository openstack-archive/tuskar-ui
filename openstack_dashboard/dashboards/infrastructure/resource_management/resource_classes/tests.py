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

from django import http
from django.core.urlresolvers import reverse
from mox import IsA
from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


class ResourceClassViewTests(test.BaseAdminViewTests):

    @test.create_stubs({
        api.management.Flavor: ('list',),
        api.management.Rack: ('list',)
    })
    def test_create_resource_class_get(self):
        all_flavors = self.management_flavors.list()
        all_racks = self.management_racks.list()

        api.management.Flavor.\
            list(IsA(http.HttpRequest)).AndReturn(all_flavors)
        api.management.Rack.\
            list(IsA(http.HttpRequest), True).AndReturn(all_racks)
        self.mox.ReplayAll()

        url = reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:create')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        api.management.ResourceClass: ('create', 'set_flavors',
                                       'set_racks'),
        api.management.Flavor: ('list',),
        api.management.Rack: ('list',)
    })
    def test_create_resource_class_post(self):
        new_resource_class = self.management_resource_classes.first()
        new_unique_name = "unique_name_for_sure"

        add_flavors_ids = []
        add_max_vms = {}
        add_racks_ids = []

        api.management.ResourceClass.\
            create(IsA(http.HttpRequest), name=new_unique_name,
                   service_type=new_resource_class.service_type).\
            AndReturn(new_resource_class)
        api.management.ResourceClass.\
            set_racks(IsA(http.HttpRequest), add_racks_ids)
        api.management.ResourceClass.\
            set_flavors(IsA(http.HttpRequest), add_flavors_ids, add_max_vms)
        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:'
                      'resource_classes:create')
        form_data = {'name': new_unique_name,
                     'service_type': new_resource_class.service_type}
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(res,
            ("%s?tab=resource_management_tabs__resource_classes_tab" %
             reverse("horizon:infrastructure:resource_management:index")))

    @test.create_stubs({api.management.ResourceClass: ('get',)})
    def test_edit_resource_class_get(self):
        resource_class = self.management_resource_classes.first()
        all_flavors = []
        all_racks = []

        api.management.ResourceClass.\
            get(IsA(http.HttpRequest), resource_class.id).MultipleTimes().\
            AndReturn(resource_class)
        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        api.management.ResourceClass.all_racks = all_racks
        api.management.ResourceClass.all_flavors = all_flavors

        url = reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:update',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        api.management.ResourceClass: ('update', 'set_racks',
                                       'set_flavors')
    })
    def test_edit_resource_class_post(self):
        resource_class = self.management_resource_classes.first()

        add_flavors_ids = []
        add_max_vms = {}
        add_racks_ids = []

        api.management.ResourceClass.\
            update(IsA(http.HttpRequest), resource_class.id,
                   name=resource_class.name,
                   service_type=resource_class.service_type).\
            AndReturn(resource_class)
        api.management.ResourceClass.\
            set_racks(IsA(http.HttpRequest), add_racks_ids)
        api.management.ResourceClass.\
            set_flavors(IsA(http.HttpRequest), add_flavors_ids, add_max_vms)
        self.mox.ReplayAll()

        form_data = {'resource_class_id': resource_class.id,
                     'name': resource_class.name,
                     'service_type': resource_class.service_type}
        url = reverse('horizon:infrastructure:resource_management:'
                     'resource_classes:update', args=[resource_class.id])
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(res,
            ("%s?tab=resource_management_tabs__resource_classes_tab" %
             reverse("horizon:infrastructure:resource_management:index")))

    @test.create_stubs({api.management.ResourceClass: ('delete', 'list')})
    def test_delete_resource_class(self):
        resource_class = self.management_resource_classes.first()
        all_resource_classes = self.management_resource_classes.list()

        api.management.ResourceClass.delete(
            IsA(http.HttpRequest),
            resource_class.id)
        api.management.ResourceClass.list(
            IsA(http.HttpRequest)).\
            AndReturn(all_resource_classes)
        self.mox.ReplayAll()

        form_data = {'action':
                     'resource_classes__delete__%s' % resource_class.id}
        res = self.client.post(
            reverse('horizon:infrastructure:resource_management:index'),
            form_data)
        self.assertRedirectsNoFollow(
            res, reverse('horizon:infrastructure:resource_management:index'))

    @test.create_stubs({
        api.management.ResourceClass: ('get', 'flavors', 'racks')
    })
    def test_detail_get(self):
        resource_class = self.management_resource_classes.first()
        flavors = []
        racks = []

        api.management.ResourceClass.get(
            IsA(http.HttpRequest),
            resource_class.id).\
            MultipleTimes().AndReturn(resource_class)
        self.mox.ReplayAll()

        api.management.ResourceClass.flavors = flavors
        api.management.ResourceClass.racks = racks

        url = reverse('horizon:infrastructure:resource_management:'
                      'resource_classes:detail', args=[resource_class.id])
        res = self.client.get(url)
        self.assertItemsEqual(res.context['flavors_table'].data,
                              flavors)
        self.assertItemsEqual(res.context['racks_table'].data,
                              racks)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
            'infrastructure/resource_management/resource_classes/detail.html')

    @test.create_stubs({api.management.ResourceClass: ('get',)})
    def test_detail_edit_racks_get(self):
        resource_class = self.management_resource_classes.first()
        all_flavors = []
        all_racks = []

        api.management.ResourceClass.\
            get(IsA(http.HttpRequest), resource_class.id).\
            MultipleTimes().AndReturn(resource_class)
        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        api.management.ResourceClass.all_racks = all_racks
        api.management.ResourceClass.all_flavors = all_flavors

        url = reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:update_racks',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        api.management.ResourceClass: ('update', 'set_racks',
                                       'set_flavors')
    })
    def test_detail_edit_racks_post(self):
        resource_class = self.management_resource_classes.first()

        add_flavors_ids = []
        add_max_vms = {}
        add_racks_ids = []

        api.management.ResourceClass.\
            update(IsA(http.HttpRequest), resource_class.id,
                   name=resource_class.name,
                   service_type=resource_class.service_type).\
            AndReturn(resource_class)
        api.management.ResourceClass.\
            set_racks(IsA(http.HttpRequest), add_racks_ids)
        api.management.ResourceClass.\
            set_flavors(IsA(http.HttpRequest), add_flavors_ids, add_max_vms)
        self.mox.ReplayAll()

        form_data = {'resource_class_id': resource_class.id,
                     'name': resource_class.name,
                     'service_type': resource_class.service_type}
        url = reverse('horizon:infrastructure:resource_management:'
                      'resource_classes:update_racks',
                      args=[resource_class.id])
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        detail_url = "horizon:infrastructure:resource_management:"\
                     "resource_classes:detail"
        redirect_url = "%s?tab=resource_class_details__racks" % (
            reverse(detail_url, args=(resource_class.id,)))
        self.assertRedirectsNoFollow(res, redirect_url)

    @test.create_stubs({api.management.ResourceClass: ('get',)})
    def test_detail_edit_flavors_get(self):
        resource_class = self.management_resource_classes.first()
        all_flavors = []
        all_racks = []

        api.management.ResourceClass.\
            get(IsA(http.HttpRequest), resource_class.id).\
            MultipleTimes().AndReturn(resource_class)
        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        api.management.ResourceClass.all_racks = all_racks
        api.management.ResourceClass.all_flavors = all_flavors

        url = reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:update_flavors',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        api.management.ResourceClass: ('update', 'set_racks',
                                       'set_flavors')
    })
    def test_detail_edit_flavors_post(self):
        resource_class = self.management_resource_classes.first()

        add_flavors_ids = []
        add_max_vms = {}
        add_racks_ids = []

        api.management.ResourceClass.\
            update(IsA(http.HttpRequest), resource_class.id,
                   name=resource_class.name,
                   service_type=resource_class.service_type).\
            AndReturn(resource_class)
        api.management.ResourceClass.\
            set_racks(IsA(http.HttpRequest), add_racks_ids)
        api.management.ResourceClass.\
            set_flavors(IsA(http.HttpRequest), add_flavors_ids, add_max_vms)
        self.mox.ReplayAll()

        form_data = {'resource_class_id': resource_class.id,
                     'name': resource_class.name,
                     'service_type': resource_class.service_type}
        url = reverse('horizon:infrastructure:resource_management:'
                      'resource_classes:update_flavors',
                      args=[resource_class.id])
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        redirect_url = "horizon:infrastructure:resource_management:"\
                       "resource_classes:detail"
        redirect_url = "%s?tab=resource_class_details__flavors" % (
            reverse(redirect_url, args=(resource_class.id,)))
        self.assertRedirectsNoFollow(res, redirect_url)

    # def test_detail_get_exception(self):
    #     index_url = reverse('horizon:infractructure:resource_management:'
    #                         'resource_classes:index')
    #     detail_url = reverse('horizon:infrastructure:resource_management:'
    #                          'resource_classes:detail', args=[42])

    #     res = self.client.get(detail_url)
    #     self.assertRedirectsNoFollow(res, index_url)
