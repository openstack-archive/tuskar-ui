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
import mock

from ceilometerclient.v2 import client as ceilometer_client
from django.core.handlers import wsgi
from django.utils import unittest
from openstack_dashboard.test import helpers

from tuskar_ui.test.test_data import utils as test_data_utils


# Makes output of failing mox tests much easier to read.
wsgi.WSGIRequest.__repr__ = lambda self: "<class 'django.http.HttpRequest'>"


# Silences the warning about with statements.
warnings.filterwarnings('ignore', 'With-statements now directly support '
                        'multiple context managers', DeprecationWarning,
                        r'^tuskar_ui[.].*[._]tests$')


create_stubs = helpers.create_stubs


class TuskarTestMixin(object):
    def _setup_test_data(self):
        super(TuskarTestMixin, self)._setup_test_data()
        # Load tuskar-specific test data.
        test_data_utils.load_test_data(self)

    def add_panel_mocks(self):
        pass  # Remove Horizon's mocks.


class NodesTestMixin(object):
    def setUp(self):
        super(NodesTestMixin, self).setUp()

        mock.patch(
            'openstack_dashboard.api.heat.heatclient',
            return_value=mock.MagicMock(**{
                'stacks.list': lambda *args, **kwargs: (
                    self.heatclient_stacks.list(),
                ),
            }),
        ).start()

    def stub_ceilometerclient(self):
        self.mox.StubOutWithMock(ceilometer_client, 'Client')
        return self.mox.CreateMock(ceilometer_client.Client)


@unittest.skipIf(os.environ.get('SKIP_UNITTESTS', False),
                 "The SKIP_UNITTESTS env variable is set.")
class TestCase(TuskarTestMixin, helpers.TestCase):
    pass


class BaseAdminViewTests(TuskarTestMixin, helpers.BaseAdminViewTests):
    pass


class APITestCase(TuskarTestMixin, helpers.APITestCase):
    pass
