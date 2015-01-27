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

from django.utils import unittest
from openstack_dashboard.test import helpers

from tuskar_ui.test.test_data import utils


# Silences the warning about with statements.
warnings.filterwarnings('ignore', 'With-statements now directly support '
                        'multiple context managers', DeprecationWarning,
                        r'^tuskar_ui[.].*[._]tests$')


def create_stubs(stubs_to_create={}):
    return helpers.create_stubs(stubs_to_create)


class TuskarTestsMixin(object):
    def _setup_test_data(self):
        super(TuskarTestsMixin, self)._setup_test_data()
        utils.load_test_data(self)

    def add_panel_mocks(self):
        pass


@unittest.skipIf(os.environ.get('SKIP_UNITTESTS', False),
                 "The SKIP_UNITTESTS env variable is set.")
class TestCase(TuskarTestsMixin, helpers.TestCase):
    pass


class BaseAdminViewTests(TuskarTestsMixin, helpers.BaseAdminViewTests):
    pass


class APITestCase(TuskarTestsMixin, helpers.APITestCase):
    pass
