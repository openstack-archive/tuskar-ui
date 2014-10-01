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
import warnings

from django.core.handlers import wsgi
from django.utils import unittest
from openstack_dashboard.test import helpers as openstack_dashboard_helpers

from tuskar_ui.test.test_data import utils as test_data_utils


# Makes output of failing mox tests much easier to read.
wsgi.WSGIRequest.__repr__ = lambda self: "<class 'django.http.HttpRequest'>"

# Silences the warning about with statements.
warnings.filterwarnings('ignore', 'With-statements now directly support '
                        'multiple context managers', DeprecationWarning,
                        r'^tuskar_ui[.].*[._]tests$')


def create_stubs(stubs_to_create={}):
    return openstack_dashboard_helpers.create_stubs(stubs_to_create)


@unittest.skipIf(os.environ.get('SKIP_UNITTESTS', False),
                 "The SKIP_UNITTESTS env variable is set.")
class TestCase(openstack_dashboard_helpers.TestCase):
    """Specialized base test case class for Horizon.

    TestCase gives access to numerous additional features:

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

        # Reload the service catalog
        tenants = self.context['authorized_tenants']
        self.setActiveUser(id=self.user.id,
                           token=self.token,
                           username=self.user.name,
                           tenant_id=self.tenant.id,
                           service_catalog=self.service_catalog,
                           authorized_tenants=tenants)


class BaseAdminViewTests(openstack_dashboard_helpers.BaseAdminViewTests):
    """A ``TestCase`` subclass which sets an active user with the "admin" role.

    This is for testing admin-only views and functionality.
    """
    def setUp(self):
        super(BaseAdminViewTests, self).setUp()

        # load tuskar-specific test data
        test_data_utils.load_test_data(self)


class APITestCase(openstack_dashboard_helpers.APITestCase):
    """TestCase for testing API clients.

    The ``APITestCase`` class is for use with tests which deal with the
    underlying clients rather than stubbing out the
    openstack_dashboard.api.* methods.
    """
    def setUp(self):
        super(APITestCase, self).setUp()

        # load tuskar-specfic test data
        test_data_utils.load_test_data(self)

        # Reload the service catalog
        tenants = self.context['authorized_tenants']
        self.setActiveUser(id=self.user.id,
                           token=self.token,
                           username=self.user.name,
                           tenant_id=self.tenant.id,
                           service_catalog=self.service_catalog,
                           authorized_tenants=tenants)
