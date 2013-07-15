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


class TuskarApiTests(test.APITestCase):
    def setUp(self):
        super(TuskarApiTests, self).setUp()
        # dummy data are seeded from fixtures
        self.rclass1 = dummymodels.ResourceClass.objects.get(name='rclass1')
        self.flavor1 = dummymodels.Flavor.objects.get(name='flavor1')

    def test_resource_class_list(self):
        rc_list = api.tuskar.ResourceClass.list(self.request)
        self.assertEquals(3, len(rc_list))
        for rc in rc_list:
            self.assertIsInstance(rc, api.tuskar.ResourceClass)

    def test_resource_class_get(self):
        rc = api.tuskar.ResourceClass.get(self.request, self.rclass1.id)
        self.assertIsInstance(rc, api.tuskar.ResourceClass)
        self.assertEquals(rc.name, self.rclass1.name)

    def test_resource_class_flavor_counts(self):
        rc = api.tuskar.ResourceClass.get(self.request, self.rclass1.id)
        for f in rc.resource_class_flavors:
            self.assertIsInstance(f, api.tuskar.ResourceClassFlavor)
        self.assertEquals(3, len(rc.resource_class_flavors))

    def test_resource_class_racks(self):
        rc = api.tuskar.ResourceClass.get(self.request, self.rclass1.id)
        for rack in rc.racks:
            self.assertIsInstance(rack, api.tuskar.Rack)
        self.assertEquals(2, len(rc.racks))

    def test_resource_class_nodes(self):
        rc = api.tuskar.ResourceClass.get(self.request, self.rclass1.id)
        for node in rc.nodes:
            self.assertIsInstance(node, api.tuskar.Node)
        self.assertEquals(4, len(rc.nodes))

    # TODO: create, delete operations

    def test_flavor_list(self):
        flist = api.tuskar.Flavor.list(self.request)
        self.assertEquals(6, len(flist))
        for f in flist:
            self.assertIsInstance(f, api.tuskar.Flavor)

    def test_flavor_get(self):
        flavor = api.tuskar.Flavor.get(self.request, self.flavor1.id)
        self.assertIsInstance(flavor, api.tuskar.Flavor)
        self.assertEquals(flavor.name, self.flavor1.name)
