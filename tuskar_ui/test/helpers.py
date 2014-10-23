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

from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware  # noqa
from django.core.handlers import wsgi
from django import http
from django.utils.importlib import import_module  # noqa
from django.utils import unittest
from horizon import middleware
import httplib2
import mox
from openstack_auth import utils
from openstack_dashboard import api
from openstack_dashboard import context_processors
from openstack_dashboard.test import helpers as openstack_dashboard_helpers
from openstack_dashboard.test.test_data import utils as test_utils

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
class InheritableDashboardTestCase(openstack_dashboard_helpers.TestCase):
    """Hack because of the self.patchers['aggregates']

    TODO(lsmola) remove this when dashboard removes the
    self.patchers['aggregates']. Which doesn't work when admin dashboard
    is not activated.
    """
    def setUp(self):
        test_utils.load_test_data(self)
        self.mox = mox.Mox()
        self.factory = openstack_dashboard_helpers.RequestFactoryWithMessages()
        self.context = {'authorized_tenants': self.tenants.list()}

        # Store the original clients
        self._original_glanceclient = api.glance.glanceclient
        self._original_keystoneclient = api.keystone.keystoneclient
        self._original_novaclient = api.nova.novaclient
        self._original_neutronclient = api.neutron.neutronclient
        self._original_cinderclient = api.cinder.cinderclient
        self._original_heatclient = api.heat.heatclient
        self._original_ceilometerclient = api.ceilometer.ceilometerclient
        self._original_troveclient = api.trove.troveclient
        self._original_saharaclient = api.sahara.client

        def fake_conn_request(*args, **kwargs):
            raise Exception("An external URI request tried to escape through "
                            "an httplib2 client. Args: %s, kwargs: %s"
                            % (args, kwargs))

        self._real_conn_request = httplib2.Http._conn_request
        httplib2.Http._conn_request = fake_conn_request

        self._real_context_processor = context_processors.openstack
        context_processors.openstack = lambda request: self.context

        self._real_get_user = utils.get_user
        tenants = self.context['authorized_tenants']
        self.setActiveUser(id=self.user.id,
                           token=self.token,
                           username=self.user.name,
                           domain_id=self.domain.id,
                           tenant_id=self.tenant.id,
                           service_catalog=self.service_catalog,
                           authorized_tenants=tenants)
        self.request = http.HttpRequest()
        self.request.session = self.client._session()
        self.request.session['token'] = self.token.id
        middleware.HorizonMiddleware().process_request(self.request)
        AuthenticationMiddleware().process_request(self.request)
        os.environ["HORIZON_TEST_RUN"] = "True"


@unittest.skipIf(os.environ.get('SKIP_UNITTESTS', False),
                 "The SKIP_UNITTESTS env variable is set.")
class TestCase(InheritableDashboardTestCase):
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


class InheritableBaseAdminViewTests(TestCase):
    """Sets an active user with the "admin" role.

    For testing admin-only views and functionality.
    """
    def setActiveUser(self, *args, **kwargs):
        if "roles" not in kwargs:
            kwargs['roles'] = [self.roles.admin._info]
        super(InheritableBaseAdminViewTests, self).setActiveUser(
            *args, **kwargs)

    def setSessionValues(self, **kwargs):
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        for key in kwargs:
            store[key] = kwargs[key]
            self.request.session[key] = kwargs[key]
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key


class BaseAdminViewTests(InheritableBaseAdminViewTests):
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
