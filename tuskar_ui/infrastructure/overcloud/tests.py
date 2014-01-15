# -*- coding: utf8 -*-
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

from django.core import urlresolvers
from mock import patch, call  # noqa

from openstack_dashboard.test.test_data import utils
from tuskar_ui import api
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:index')
TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)


class OvercloudTests(test.BaseAdminViewTests):
    def test_index_get_undeployed(self):
        stack = api.Overcloud(TEST_DATA.heatclient_stacks.first)
        with patch('tuskar_ui.api.Overcloud', **{
            'spec_set': ['get', 'is_deployed'],
            'is_deployed': False,
            'get.return_value': stack,
        }) as Overcloud:
            res = self.client.get(INDEX_URL)
            request = Overcloud.get.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Overcloud.get.call_args_list, [call(request)])

        self.assertTemplateUsed(
            res, 'infrastructure/_fullscreen_workflow_base.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/undeployed_overview.html')
