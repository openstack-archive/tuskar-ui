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

from django import http
from django.core.urlresolvers import reverse

from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


class ResourceManagementTests(test.BaseAdminViewTests):
    def setUp(self):
        super(ResourceManagementTests, self).setUp()

    @test.create_stubs({
        api.management.ResourceClass: (
            'list',
            'racks',
            'hosts'),
        api.management.Flavor: (
            'list',)})
    def test_index(self):
        # Flavor stubs
        flavors = self.management_flavors.list()

        api.management.Flavor.list(IsA(http.HttpRequest)).AndReturn(flavors)
        # Flavor stubs end

        # ResourceClass stubs
        all_resource_classes = self.management_resource_classes.list()
        hosts = []
        racks = []

        api.management.ResourceClass.hosts = hosts
        api.management.ResourceClass.racks = racks

        api.management.ResourceClass.list(
            IsA(http.HttpRequest)).\
            AndReturn(all_resource_classes)
        # ResourceClass stubs end

        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:index')
        res = self.client.get(url)
        self.assertTemplateUsed(
            res, 'infrastructure/resource_management/index.html')

        # Flavor asserts
        self.assertItemsEqual(res.context['flavors_table'].data, flavors)
        # Flavor asserts end

        # ResourceClass asserts
        self.assertItemsEqual(res.context['resource_classes_table'].data,
                              all_resource_classes)
        # ResourceClass asserts end
