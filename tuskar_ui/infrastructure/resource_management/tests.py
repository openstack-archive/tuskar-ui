# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
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

from django.core.urlresolvers import reverse
from django import http

from mox import IsA

from tuskar_ui import api
from openstack_dashboard.test import helpers as test


class ResourceManagementTests(test.BaseAdminViewTests):
    def setUp(self):
        super(ResourceManagementTests, self).setUp()

    @test.create_stubs({
        api.tuskar.ResourceClass: (
            'get',
            'list',
            'list_racks',
            'nodes'),
        api.tuskar.FlavorTemplate: (
            'list',),
        api.tuskar.Node: (
            'list',),
        api.tuskar.Rack: (
            'list',)})
    def test_index(self):

        # ResourceClass stubs
        resource_classes = self.tuskar_resource_classes.list()
        resource_class = self.tuskar_resource_classes.first()
        nodes = []
        racks = []

        api.tuskar.ResourceClass.nodes = nodes
        api.tuskar.ResourceClass.list_racks = racks

        api.tuskar.ResourceClass.list(
            IsA(http.HttpRequest)).\
            AndReturn(resource_classes)

        api.tuskar.ResourceClass.get(
            IsA(http.HttpRequest), resource_class.id).\
            AndReturn(resource_class)
        # ResourceClass stubs end

        # Rack stubs
        racks = self.tuskar_racks.list()

        api.tuskar.Rack.list(IsA(http.HttpRequest)).AndReturn(racks)
        api.tuskar.Node.list(IsA(http.HttpRequest)).AndReturn(nodes)
        # Rack stubs end

        # FlavorTemplate stubs
        flavors = self.tuskar_flavors.list()

        api.tuskar.FlavorTemplate.list(IsA(http.HttpRequest)).AndReturn(
                flavors)
        # FlavorTemplate stubs end

        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:index')
        res = self.client.get(url)
        self.assertTemplateUsed(
            res, 'infrastructure/resource_management/index.html')

        # FlavorTemplate asserts
        self.assertItemsEqual(res.context['flavors_table'].data, flavors)
        # FlavorTemplate asserts end

        # ResourceClass asserts
        self.assertItemsEqual(res.context['resource_classes_table'].data,
                              resource_classes)
        # ResourceClass asserts end

        # Rack asserts
        self.assertItemsEqual(res.context['racks_table'].data, racks)
        # Rack asserts end
