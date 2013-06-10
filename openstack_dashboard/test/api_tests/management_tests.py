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

from __future__ import absolute_import

from django import http
from django.conf import settings
from django.test.utils import override_settings

from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test
import openstack_dashboard.dashboards.infrastructure.models as dummymodels


class ManagementApiTests(test.APITestCase):
    def setUp(self):
        super(ManagementApiTests, self).setUp()
        # dummy data are seeded from fixtures
        self.rclass1 = dummymodels.ResourceClass.objects.get(name='rclass1')
        self.flavor1 = dummymodels.Flavor.objects.get(name='flavor1')

    def test_resource_class_list(self):
        rc_list = api.management.resource_class_list(self.request)
        self.assertEquals(3, len(rc_list))
        for rc in rc_list:
            self.assertIsInstance(rc, api.management.ResourceClass)

    def test_resource_class_get(self):
        rc = api.management.resource_class_get(self.request, self.rclass1.id)
        self.assertIsInstance(rc, api.management.ResourceClass)
        self.assertEquals(rc.name, self.rclass1.name)

    def test_resource_class_flavors(self):
        rc = api.management.resource_class_get(self.request, self.rclass1.id)
        for f in rc.flavors:
            self.assertIsInstance(f, api.management.Flavor)
        self.assertEquals(1, len(rc.flavors))

    def test_resource_class_racks(self):
        rc = api.management.resource_class_get(self.request, self.rclass1.id)
        for rack in rc.racks:
            self.assertIsInstance(rack, api.management.Rack)
        self.assertEquals(2, len(rc.racks))

    def test_resource_class_hosts(self):
        rc = api.management.resource_class_get(self.request, self.rclass1.id)
        for host in rc.hosts:
            self.assertIsInstance(host, api.management.Host)
        self.assertEquals(4, len(rc.hosts))

    # TODO: create, delete operations

    def test_flavor_list(self):
        flist = api.management.flavor_list(self.request)
        self.assertEquals(1, len(flist))
        for f in flist:
            self.assertIsInstance(f, api.management.Flavor)

    def test_flavor_get(self):
        flavor = api.management.flavor_get(self.request, self.flavor1.id)
        self.assertIsInstance(flavor, api.management.Flavor)
        self.assertEquals(flavor.name, self.flavor1.name)
