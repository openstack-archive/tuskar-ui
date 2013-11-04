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


class ResourceManagementTests(test.BaseAdminViewTests):
    index_page = urlresolvers.reverse(
        'horizon:infrastructure:resource_management:index')

    def setUp(self):
        super(ResourceManagementTests, self).setUp()

    @test.create_stubs({
        tuskar.ResourceClass: ('get', 'list', 'list_racks', 'tuskar_nodes'),
        tuskar.TuskarNode: ('list',),
        tuskar.Rack: ('list',),
    })
    def test_index(self):

        # ResourceClass stubs
        resource_classes = self.tuskar_resource_classes.list()
        resource_class = self.tuskar_resource_classes.first()
        tuskar_nodes = []
        racks = []

        tuskar.ResourceClass.tuskar_nodes = tuskar_nodes
        tuskar.ResourceClass.list_racks = racks

        tuskar.Rack.list(mox.IsA(http.HttpRequest)).AndReturn(racks)
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(resource_classes)

        tuskar.ResourceClass.get(
            mox.IsA(http.HttpRequest),
            resource_class.id).AndReturn(resource_class)
        # ResourceClass stubs end

        # Rack stubs
        racks = self.tuskar_racks.list()

        tuskar.Rack.list(mox.IsA(http.HttpRequest)).AndReturn(racks)
        tuskar.Rack.list(mox.IsA(http.HttpRequest)).AndReturn(racks)
        tuskar.TuskarNode.list(
            mox.IsA(http.HttpRequest)).AndReturn(tuskar_nodes)
        # Rack stubs end

        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:index')
        res = self.client.get(url)
        self.assertTemplateUsed(
            res, 'infrastructure/resource_management/index.html')

        # ResourceClass asserts
        self.assertItemsEqual(res.context['resource_classes_table'].data,
                              resource_classes)
        # ResourceClass asserts end

        # Rack asserts
        self.assertItemsEqual(res.context['racks_table'].data, racks)
        # Rack asserts end

    @test.create_stubs({tuskar.Rack: ('provision_all',)})
    def test_provision_post(self):
        tuskar.Rack.provision_all(mox.IsA(http.HttpRequest))

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:provision',
                                   args=[])
        response = self.client.post(url)

        self.assertNoFormErrors(response)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(response, self.index_page)
