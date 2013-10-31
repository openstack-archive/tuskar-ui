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

import os

from django.core.handlers import wsgi
from django.utils import unittest

from novaclient.v1_1.contrib import baremetal
from tuskarclient.v1 import client as tuskar_client

from openstack_dashboard.test import helpers as openstack_dashboard_helpers
from tuskar_ui import api as tuskar_api
from tuskar_ui.test.test_data import utils as test_data_utils


# Makes output of failing mox tests much easier to read.
wsgi.WSGIRequest.__repr__ = lambda self: "<class 'django.http.HttpRequest'>"


def create_stubs(stubs_to_create={}):
    return openstack_dashboard_helpers.create_stubs(stubs_to_create)


@unittest.skipIf(os.environ.get('SKIP_UNITTESTS', False),
                 "The SKIP_UNITTESTS env variable is set.")
class TestCase(openstack_dashboard_helpers.TestCase):
    """Specialized base test case class for Horizon which gives access to
    numerous additional features:

      * A full suite of test data through various attached objects and
        managers (e.g. ``self.servers``, ``self.user``, etc.). See the
        docs for :class:`~horizon.tests.test_data.utils.TestData` for more
        information.
      * The ``mox`` mocking framework via ``self.mox``.
      * A set of request context data via ``self.context``.
      * A ``RequestFactory`` class which supports Django's ``contrib.messages``
        framework via ``self.factory``.
      * A ready-to-go request object via ``self.request``.
      * The ability to override specific time data controls for easier testing.
      * Several handy additional assertion methods.
    """
    def setUp(self):
        super(TestCase, self).setUp()

        # load tuskar-specific test data
        test_data_utils.load_test_data(self)


class BaseAdminViewTests(openstack_dashboard_helpers.BaseAdminViewTests):
    """A ``TestCase`` subclass which sets an active user with the "admin" role
    for testing admin-only views and functionality.
    """
    def setUp(self):
        super(BaseAdminViewTests, self).setUp()

        # load tuskar-specific test data
        test_data_utils.load_test_data(self)


class APITestCase(openstack_dashboard_helpers.APITestCase):
    """The ``APITestCase`` class is for use with tests which deal with the
    underlying clients rather than stubbing out the
    openstack_dashboard.api.* methods.
    """
    def setUp(self):
        super(APITestCase, self).setUp()

        # load tuskar-specfic test data
        test_data_utils.load_test_data(self)

        # Store the original clients
        self._original_tuskarclient = tuskar_api.tuskarclient
        self._original_baremetalclient = tuskar_api.baremetalclient

        # Replace the clients with our stubs.
        tuskar_api.tuskarclient = lambda request: self.stub_tuskarclient()
        tuskar_api.baremetalclient = lambda request:\
            self.stub_baremetalclient()

    def tearDown(self):
        super(APITestCase, self).tearDown()
        tuskar_api.tuskarclient = self._original_tuskarclient
        tuskar_api.baremetalclient = self._original_baremetalclient

    def stub_tuskarclient(self):
        if not hasattr(self, "tuskarclient"):
            self.mox.StubOutWithMock(tuskar_client, 'Client')
            self.tuskarclient = self.mox.CreateMock(tuskar_client.Client)
        return self.tuskarclient

    def stub_baremetalclient(self):
        if not hasattr(self, "baremetalclient"):
            self.baremetalclient = baremetal.BareMetalNodeManager(None)
        return self.baremetalclient
