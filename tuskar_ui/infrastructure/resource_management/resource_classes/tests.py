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


class ResourceClassViewTests(test.BaseAdminViewTests):

    @test.create_stubs({
        tuskar.FlavorTemplate: ('list',),
        tuskar.Rack: ('list',),
        tuskar.ResourceClass: ('get',)
    })
    def test_create_resource_class_get(self):
        all_templates = self.tuskar_flavor_templates.list()
        all_racks = self.tuskar_racks.list()
        rc = self.tuskar_resource_classes.first()

        tuskar.FlavorTemplate.list(
            mox.IsA(http.HttpRequest)).AndReturn(all_templates)
        tuskar.Rack.list(
            mox.IsA(http.HttpRequest), True).AndReturn(all_racks)
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), rc.id).AndReturn(rc)
        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'create')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('list', 'create', 'set_racks'),
    })
    def test_create_resource_class_post(self):
        new_resource_class = self.tuskar_resource_classes.first()
        new_unique_name = "unique_name_for_sure"
        new_flavors = []

        add_racks_ids = []

        tuskar.ResourceClass.list(
            mox.IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.create(
            mox.IsA(http.HttpRequest),
            name=new_unique_name,
            service_type=new_resource_class.service_type,
            flavors=new_flavors).AndReturn(new_resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'create')
        form_data = {'name': new_unique_name,
                     'service_type': new_resource_class.service_type,
                     'image': 'compute-img'}
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        redirect_url = (
            "%s?tab=resource_management_tabs__resource_classes_tab" %
                urlresolvers.reverse('horizon:infrastructure:'
                                            'resource_management:index'))
        self.assertRedirectsNoFollow(res, redirect_url)

    @test.create_stubs({tuskar.ResourceClass: ('get', 'list_flavors',
                                                   'racks_ids', 'all_racks',
                                                   'all_flavors')})
    def test_edit_resource_class_get(self):
        resource_class = self.tuskar_resource_classes.first()
        all_flavors = []
        all_racks = []

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
                    resource_class.id).MultipleTimes().AndReturn(
                        resource_class)

        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        tuskar.ResourceClass.all_racks = all_racks
        tuskar.ResourceClass.all_flavors = all_flavors
        tuskar.ResourceClass.list_flavors = all_flavors

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'update',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list', 'update', 'set_racks')
    })
    def test_edit_resource_class_post(self):
        resource_class = self.tuskar_resource_classes.first()

        add_racks_ids = []

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.list(
            mox.IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.update(mox.IsA(http.HttpRequest),
                                    resource_class.id,
                                    name=resource_class.name,
                                    service_type=resource_class.service_type,
                                    flavors=[]).AndReturn(resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        form_data = {'resource_class_id': resource_class.id,
                     'name': resource_class.name,
                     'service_type': resource_class.service_type,
                     'image': 'compute-img'}
        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'update',
            args=[resource_class.id])
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        redirect_url = (
            "%s?tab=resource_management_tabs__resource_classes_tab" %
                urlresolvers.reverse('horizon:infrastructure:'
                                            'resource_management:index'))
        self.assertRedirectsNoFollow(res, redirect_url)

    @test.create_stubs({tuskar.ResourceClass: ('delete', 'list')})
    def test_delete_resource_class(self):
        resource_class = self.tuskar_resource_classes.first()
        all_resource_classes = self.tuskar_resource_classes.list()

        tuskar.ResourceClass.delete(mox.IsA(http.HttpRequest),
                                    resource_class.id)
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(all_resource_classes)
        self.mox.ReplayAll()

        form_data = {'action':
                     'resource_classes__delete__%s' % resource_class.id}
        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:index')
        res = self.client.post(url, form_data)

        redirect_url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:index')
        self.assertRedirectsNoFollow(res, redirect_url)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_flavors', 'list_racks')
    })
    def test_detail_get(self):
        resource_class = self.tuskar_resource_classes.first()
        flavors = []
        racks = []

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).\
                MultipleTimes().AndReturn(resource_class)
        self.mox.ReplayAll()

        tuskar.ResourceClass.list_flavors = flavors
        tuskar.ResourceClass.list_racks = racks

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'detail',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertItemsEqual(res.context['flavors_table'].data,
                              flavors)
        self.assertItemsEqual(res.context['racks_table'].data,
                              racks)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
            'infrastructure/resource_management/resource_classes/detail.html')

    @test.create_stubs({tuskar.ResourceClass: ('get', 'list_flavors',
                                                   'racks_ids', 'all_racks',
                                                   'all_flavors')})
    def test_detail_edit_racks_get(self):
        resource_class = self.tuskar_resource_classes.first()
        all_flavors = []
        all_racks = []

        tuskar.ResourceClass.get(mox.IsA(http.HttpRequest),
                                 resource_class.id).\
               MultipleTimes().AndReturn(resource_class)
        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        tuskar.ResourceClass.all_racks = all_racks
        tuskar.ResourceClass.all_flavors = all_flavors
        tuskar.ResourceClass.list_flavors = all_flavors

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'update_racks',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list', 'update', 'set_racks')
    })
    def test_detail_edit_racks_post(self):
        resource_class = self.tuskar_resource_classes.first()

        add_racks_ids = []

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.list(
            mox.IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.update(mox.IsA(http.HttpRequest),
                                    resource_class.id,
                                    name=resource_class.name,
                                    service_type=resource_class.service_type,
                                    flavors=[]).AndReturn(resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        form_data = {'resource_class_id': resource_class.id,
                     'name': resource_class.name,
                     'service_type': resource_class.service_type,
                     'image': 'compute-img'}
        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'update_racks',
            args=[resource_class.id])
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        detail_url = ('horizon:infrastructure:resource_management:'
                      'resource_classes:detail')
        redirect_url = (
            "%s?tab=resource_class_details__racks" %
                urlresolvers.reverse(detail_url, args=(resource_class.id,)))
        self.assertRedirectsNoFollow(res, redirect_url)

    @test.create_stubs({tuskar.ResourceClass: ('get', 'list_flavors',
                                                   'racks_ids', 'all_racks',
                                                   'all_flavors')})
    def test_detail_edit_flavors_get(self):
        resource_class = self.tuskar_resource_classes.first()
        all_flavors = []
        all_racks = []

        tuskar.ResourceClass.get(mox.IsA(http.HttpRequest),
                                 resource_class.id).\
               MultipleTimes().AndReturn(resource_class)
        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        tuskar.ResourceClass.all_racks = all_racks
        tuskar.ResourceClass.all_flavors = all_flavors
        tuskar.ResourceClass.list_flavors = all_flavors

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'update_flavors',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list', 'update', 'set_racks')
    })
    def test_detail_edit_flavors_post(self):
        resource_class = self.tuskar_resource_classes.first()

        add_racks_ids = []

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.list(
            mox.IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.update(mox.IsA(http.HttpRequest),
                                    resource_class.id,
                                    name=resource_class.name,
                                    service_type=resource_class.service_type,
                                    flavors=[]).AndReturn(resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        form_data = {'resource_class_id': resource_class.id,
                     'name': resource_class.name,
                     'service_type': resource_class.service_type,
                     'image': 'compute-img'}
        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
                'update_flavors',
            args=[resource_class.id])
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        redirect_url = ('horizon:infrastructure:resource_management:'
                            'resource_classes:detail')
        redirect_url = "%s?tab=resource_class_details__flavors" % (
            urlresolvers.reverse(redirect_url, args=(resource_class.id,)))
        self.assertRedirectsNoFollow(res, redirect_url)

    # def test_detail_get_exception(self):
    #     index_url = reverse('horizon:infractructure:resource_management:'
    #                         'resource_classes:index')
    #     detail_url = reverse('horizon:infrastructure:resource_management:'
    #                          'resource_classes:detail', args=[42])

    #     res = self.client.get(detail_url)
    #     self.assertRedirectsNoFollow(res, index_url)
