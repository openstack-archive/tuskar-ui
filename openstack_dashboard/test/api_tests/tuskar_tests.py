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
    def test_resource_class_list(self):
        rcs = self.tuskar_resource_classes.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.list().AndReturn(rcs)
        self.mox.ReplayAll()

        ret_val = api.tuskar.ResourceClass.list(self.request)
        for rc in ret_val:
            self.assertIsInstance(rc, api.tuskar.ResourceClass)

    def test_resource_class_get(self):
        rc = self.tuskar_resource_classes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.resource_classes = self.mox.CreateMockAnything()
        tuskarclient.resource_classes.get(rc.id).AndReturn(rc)
        self.mox.ReplayAll()

        ret_val = api.tuskar.ResourceClass.get(self.request, rc.id)
        self.assertIsInstance(ret_val, api.tuskar.ResourceClass)

    def test_resource_class_flavor_counts(self):
        rc = self.tuskar_resource_classes.first()
        flavors = self.tuskar_flavors.list()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.flavors = self.mox.CreateMockAnything()
        tuskarclient.flavors.list(rc.id).AndReturn(flavors)
        self.mox.ReplayAll()

        for f in rc.list_flavors:
            self.assertIsInstance(f, api.tuskar.Flavor)
        self.assertEquals(2, len(rc.list_flavors))

    def test_resource_class_racks(self):
        rc = self.tuskar_resource_classes.first()
        r = self.tuskar_racks.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get(r.id).AndReturn(r)
        self.mox.ReplayAll()

        for rack in rc.list_racks:
            self.assertIsInstance(rack, api.tuskar.Rack)
        self.assertEquals(1, len(rc.list_racks))

    ## FIXME: we need to stub out the bare metal client, will
    ## be easier once the client is separated out a bit
    def test_resource_class_nodes(self):
        rc = self.tuskar_resource_classes.first()
        r = self.tuskar_racks.first()
        n = self.nodes.first()

        tuskarclient = self.stub_tuskarclient()
        tuskarclient.racks = self.mox.CreateMockAnything()
        tuskarclient.racks.get(r.id).AndReturn(r)
        self.mox.ReplayAll()

        for node in rc.nodes:
            self.assertIsInstance(node, api.tuskar.Node)
        self.assertEquals(4, len(rc.nodes))

    # TODO: create, delete operations

    def test_flavor_template_list(self):
        templates = api.tuskar.FlavorTemplate.list(self.request)
        self.assertEquals(7, len(templates))
        for t in templates:
            self.assertIsInstance(t, api.tuskar.FlavorTemplate)

    def test_flavor_template_get(self):
        test_template = self.tuskar_flavor_templates.first()
        template = api.tuskar.FlavorTemplate.get(self.request,
                                                 test_template.id)
        self.assertIsInstance(template, api.tuskar.FlavorTemplate)
        self.assertEquals(template.name, test_template.name)
