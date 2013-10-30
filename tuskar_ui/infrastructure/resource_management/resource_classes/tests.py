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
from django.utils import simplejson

import mox

from openstack_dashboard.api import glance
from openstack_dashboard.test.test_data import glance_data

from tuskar_ui import api as tuskar
from tuskar_ui.test import helpers as test


class ResourceClassViewTests(test.BaseAdminViewTests):
    def setUp(self):
        super(ResourceClassViewTests, self).setUp()
        # Add the .images attribute for testing glance api call
        glance_data.data(self)

    @test.create_stubs({
        tuskar.Rack: ('list',),
        tuskar.ResourceClass: ('get',),
        glance: ('image_list_detailed',),
    })
    def test_create_resource_class_get(self):
        all_racks = self.tuskar_racks.list()
        rc = self.tuskar_resource_classes.first()

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
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
        tuskar.Rack: ('list',),
        glance: ('image_list_detailed',),
    })
    def test_create_resource_class_post(self):
        new_resource_class = self.tuskar_resource_classes.first()
        new_unique_name = "unique_name_for_sure"
        new_flavors = []
        image_id = self.images.list()[0].id

        add_racks_ids = []

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.Rack.list(
            mox.IsA(http.HttpRequest), True).AndReturn([])
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.create(
            mox.IsA(http.HttpRequest),
            name=new_unique_name,
            service_type=new_resource_class.service_type,
            image_id=image_id,
            flavors=new_flavors).AndReturn(new_resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
            'create')
        form_data = {
            'name': new_unique_name,
            'service_type': new_resource_class.service_type,
            'image_id': image_id,
            'flavors-TOTAL_FORMS': 0,
            'flavors-INITIAL_FORMS': 0,
            'flavors-MAX_NUM_FORMS': 1000,
            'racks-TOTAL_FORMS': 0,
            'racks-INITIAL_FORMS': 0,
            'racks-MAX_NUM_FORMS': 1000,
        }
        res = self.client.post(url, form_data)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        redirect_url = (
            "%s?tab=resource_management_tabs__resource_classes_tab" %
            urlresolvers.reverse('horizon:infrastructure:'
                                 'resource_management:index'))
        self.assertRedirectsNoFollow(res, redirect_url)

    @test.create_stubs({
        tuskar.ResourceClass: ('list', 'create', 'set_racks'),
        tuskar.Rack: ('list',),
        glance: ('image_list_detailed',),
    })
    def test_create_resource_class_post_exception(self):
        new_resource_class = self.tuskar_resource_classes.first()
        new_unique_name = "unique_name_for_sure"
        new_flavors = []
        image_id = self.images.list()[0].id

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.Rack.list(
            mox.IsA(http.HttpRequest), True).AndReturn([])
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.\
            create(mox.IsA(http.HttpRequest), name=new_unique_name,
                   service_type=new_resource_class.service_type,
                   image_id=image_id,
                   flavors=new_flavors).\
            AndRaise(self.exceptions.tuskar)
        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:create')
        form_data = {
            'name': new_unique_name,
            'service_type': new_resource_class.service_type,
            'image_id': image_id,
            'flavors-TOTAL_FORMS': 0,
            'flavors-INITIAL_FORMS': 0,
            'flavors-MAX_NUM_FORMS': 1000,
            'racks-TOTAL_FORMS': 0,
            'racks-INITIAL_FORMS': 0,
            'racks-MAX_NUM_FORMS': 1000,
        }
        res = self.client.post(url, form_data)
        self.assertRedirectsNoFollow(
            res,
            ("%s?tab=resource_management_tabs__resource_classes_tab" %
             urlresolvers.
             reverse("horizon:infrastructure:resource_management:index")))

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_flavors', 'racks_ids',
                               'all_racks'),
        glance: ('image_list_detailed',),
    })
    def test_edit_resource_class_get(self):
        resource_class = self.tuskar_resource_classes.first()
        all_flavors = []
        all_racks = []

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        # get_flavors_data in workflows.py
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        # get_racks_data in workflows.py
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        tuskar.ResourceClass.all_racks = all_racks
        tuskar.ResourceClass.list_flavors = all_flavors

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
            'update',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_flavors',
                               'racks_ids', 'all_racks'),
        glance: ('image_list_detailed',),
    })
    def test_edit_resource_class_get_exception(self):
        resource_class = self.tuskar_resource_classes.first()

        tuskar.ResourceClass.\
            get(mox.IsA(http.HttpRequest), resource_class.id)\
            .AndRaise(self.exceptions.tuskar)

        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:update',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertRedirectsNoFollow(
            res, urlresolvers.reverse(
                'horizon:infrastructure:resource_management:index'))

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list', 'update', 'set_racks',
                               'list_flavors', 'all_racks', 'racks_ids'),
        tuskar.Rack: ('list',),
        glance: ('image_list_detailed',),
    })
    def test_edit_resource_class_post(self):
        resource_class = self.tuskar_resource_classes.first()
        image_id = self.images.list()[0].id

        add_racks_ids = []

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.all_racks = []
        tuskar.ResourceClass.racks_ids = []
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.list_flavors = []
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.update(mox.IsA(http.HttpRequest),
                                    resource_class.id,
                                    name=resource_class.name,
                                    service_type=resource_class.service_type,
                                    image_id=image_id,
                                    flavors=[]).AndReturn(resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        form_data = {
            'resource_class_id': resource_class.id,
            'name': resource_class.name,
            'service_type': resource_class.service_type,
            'image_id': image_id,
            'flavors-TOTAL_FORMS': 0,
            'flavors-INITIAL_FORMS': 0,
            'flavors-MAX_NUM_FORMS': 1000,
            'racks-TOTAL_FORMS': 0,
            'racks-INITIAL_FORMS': 0,
            'racks-MAX_NUM_FORMS': 1000,
        }
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

    @test.create_stubs({tuskar.ResourceClass: ('delete', 'list')})
    def test_delete_resource_class_exception(self):
        resource_class = self.tuskar_resource_classes.first()
        all_resource_classes = self.tuskar_resource_classes.list()

        tuskar.ResourceClass.delete(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndRaise(self.exceptions.tuskar)
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).\
            AndReturn(all_resource_classes)
        self.mox.ReplayAll()

        form_data = {'action':
                     'resource_classes__delete__%s' % resource_class.id}
        res = self.client.post(
            urlresolvers.reverse(
                'horizon:infrastructure:resource_management:index'),
            form_data)
        # FIXME: there should be a better test than this, but the message
        # is unreadable in a redirect response
        self.assertRedirectsNoFollow(
            res, urlresolvers.reverse(
                'horizon:infrastructure:resource_management:index'))

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_flavors', 'list_racks',
                               'tuskar_nodes')
    })
    def test_detail_get(self):
        resource_class = self.tuskar_resource_classes.first()
        flavors = []
        racks = []

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).\
            AndReturn(resource_class)
        self.mox.ReplayAll()

        tuskar.ResourceClass.list_flavors = flavors
        tuskar.ResourceClass.list_racks = racks
        tuskar.ResourceClass.tuskar_nodes = []

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
            'detail',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertItemsEqual(res.context['flavors_table_table'].data, flavors)
        self.assertItemsEqual(res.context['racks_table_table'].data, racks)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(
            res,
            'infrastructure/resource_management/resource_classes/detail.html')

    @test.create_stubs({
        tuskar.ResourceClass: ('get',)
    })
    def test_detail_action_get(self):
        resource_class = self.tuskar_resource_classes.first()

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
            'detail_action', args=[resource_class.id]) + "?action=delete"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'delete')
    })
    def test_detail_action_post(self):
        resource_class = self.tuskar_resource_classes.first()

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)
        tuskar.ResourceClass.delete(mox.IsA(http.HttpRequest),
                                    resource_class.id)

        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
            'detail_action', args=[resource_class.id]) + "?action=delete"
        res = self.client.post(url)
        self.assertNoFormErrors(res)
        self.assertMessageCount(success=1)

        redirect_url = urlresolvers.reverse('horizon:infrastructure:'
                                            'resource_management:index')
        self.assertRedirectsNoFollow(res, redirect_url)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_racks')
    })
    def test_rack_health_get(self):
        resource_class = self.tuskar_resource_classes.first()
        racks = [self.tuskar_racks.first()]
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).\
            AndReturn(resource_class)
        self.mox.ReplayAll()

        tuskar.ResourceClass.list_racks = racks

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:rack_health', args=[resource_class.id])
        res = self.client.get(url)
        data = simplejson.loads(res.content)['data']

        # FIXME: this is dummy data right now, just assert its presence
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'rack1')

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_flavors', 'list_racks')
    })
    def test_detail_get_exception(self):
        resource_class = self.tuskar_resource_classes.first()

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).\
            AndRaise(self.exceptions.tuskar)
        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:detail', args=[resource_class.id])
        res = self.client.get(url)
        self.assertRedirectsNoFollow(
            res, urlresolvers.reverse(
                'horizon:infrastructure:resource_management:index'))

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_flavors',
                               'racks_ids', 'all_racks'),
        glance: ('image_list_detailed',),
    })
    def test_detail_edit_racks_get(self):
        resource_class = self.tuskar_resource_classes.first()
        all_flavors = []
        all_racks = []

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.ResourceClass.get(mox.IsA(http.HttpRequest),
                                 resource_class.id).AndReturn(resource_class)

        # get_flavors_data in workflows.py
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        # get_racks_data in workflows.py
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        tuskar.ResourceClass.all_racks = all_racks
        tuskar.ResourceClass.list_flavors = all_flavors

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
            'update_racks',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list', 'update', 'set_racks',
                               'list_flavors', 'all_racks', 'racks_ids'),
        glance: ('image_list_detailed',),
    })
    def test_detail_edit_racks_post(self):
        resource_class = self.tuskar_resource_classes.first()
        image_id = self.images.list()[0].id
        add_racks_ids = []

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.all_racks = []
        tuskar.ResourceClass.racks_ids = []
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.list_flavors = []
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.update(mox.IsA(http.HttpRequest),
                                    resource_class.id,
                                    name=resource_class.name,
                                    service_type=resource_class.service_type,
                                    image_id=image_id,
                                    flavors=[]).AndReturn(resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        form_data = {
            'resource_class_id': resource_class.id,
            'name': resource_class.name,
            'service_type': resource_class.service_type,
            'image_id': image_id,
            'flavors-TOTAL_FORMS': 0,
            'flavors-INITIAL_FORMS': 0,
            'flavors-MAX_NUM_FORMS': 1000,
            'racks-TOTAL_FORMS': 0,
            'racks-INITIAL_FORMS': 0,
            'racks-MAX_NUM_FORMS': 1000,
        }
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

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list_flavors',
                               'racks_ids', 'all_racks'),
        glance: ('image_list_detailed',),
    })
    def test_detail_edit_flavors_get(self):
        resource_class = self.tuskar_resource_classes.first()
        all_flavors = []
        all_racks = []

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.ResourceClass.get(mox.IsA(http.HttpRequest),
                                 resource_class.id).AndReturn(resource_class)

        # get_flavors_data in workflows.py
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        # get_racks_data in workflows.py
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)

        self.mox.ReplayAll()

        # FIXME I should probably track the racks and flavors methods
        # so maybe they shouldn't be a @property
        # properties set
        tuskar.ResourceClass.all_racks = all_racks
        tuskar.ResourceClass.list_flavors = all_flavors

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:resource_classes:'
            'update_flavors',
            args=[resource_class.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list', 'update', 'set_racks',
                               'list_flavors', 'all_racks', 'racks_ids'),
        tuskar.Rack: ('list',),
        glance: ('image_list_detailed',),
    })
    def test_detail_edit_flavors_post(self):
        resource_class = self.tuskar_resource_classes.first()
        image_id = self.images.list()[0].id
        add_racks_ids = []

        glance.image_list_detailed(mox.IsA(http.HttpRequest)).AndReturn(
            (self.images.list(), False))
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.all_racks = []
        tuskar.ResourceClass.racks_ids = []
        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest), resource_class.id).AndReturn(
                resource_class)
        tuskar.ResourceClass.list_flavors = []
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        tuskar.ResourceClass.update(mox.IsA(http.HttpRequest),
                                    resource_class.id,
                                    name=resource_class.name,
                                    service_type=resource_class.service_type,
                                    image_id=image_id,
                                    flavors=[]).AndReturn(resource_class)
        tuskar.ResourceClass.set_racks(mox.IsA(http.HttpRequest),
                                       add_racks_ids)
        self.mox.ReplayAll()

        form_data = {
            'resource_class_id': resource_class.id,
            'name': resource_class.name,
            'service_type': resource_class.service_type,
            'image_id': image_id,
            'flavors-TOTAL_FORMS': 0,
            'flavors-INITIAL_FORMS': 0,
            'flavors-MAX_NUM_FORMS': 1000,
            'racks-TOTAL_FORMS': 0,
            'racks-INITIAL_FORMS': 0,
            'racks-MAX_NUM_FORMS': 1000,
        }
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
