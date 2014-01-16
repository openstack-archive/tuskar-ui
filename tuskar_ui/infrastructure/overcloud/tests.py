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
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:create')
DETAIL_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:create')
TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)


class OvercloudTests(test.BaseAdminViewTests):

    def test_index_overcloud_undeployed_get(self):
        oc = api.Overcloud(TEST_DATA.tuskarclient_overclouds.first())
        with patch('tuskar_ui.api.Overcloud', **{
            'spec_set': ['get', 'is_deployed'],
            'is_deployed': False,
            'get.return_value': oc,
        }) as Overcloud:
            res = self.client.get(INDEX_URL)
            request = Overcloud.get.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Overcloud.get.call_args_list,
                                 [call(request, 1)])
        self.assertRedirectsNoFollow(res, CREATE_URL)

    def test_create_overcloud_undeployed_post(self):
        oc = api.Overcloud(TEST_DATA.tuskarclient_overclouds.first())
        data = {
            'count__controller__default': '1',
            'count__compute__default': '0',
            'count__object_storage__default': '0',
            'count__block_storage__default': '0',
            'mysql_host_ip': '',
            'mysql_user': 'admin',
            'mysql_password': 'pass',
            'amqp_host_ip': '',
            'amqp_password': 'pass',
            'keystone_host_ip': '',
            'keystone_db_password': 'pass',
            'keystone_admin_token': 'pass',
            'keystone_admin_password': 'pass',
        }
        with patch('tuskar_ui.api.Overcloud', **{
            'spec_set': ['create'],
            'create.return_value': oc,
        }) as Overcloud:
            res = self.client.post(CREATE_URL, data)
            request = Overcloud.create.call_args_list[0][0][0]
            self.assertListEqual(
                Overcloud.create.call_args_list,
                [
                    call(request, {
                        ('controller', 'default'): 1,
                        ('compute', 'default'): 0,
                        ('object_storage', 'default'): 0,
                        ('block_storage', 'default'): 0,
                    }),
                ])
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_index_overcloud_deployed(self):
        oc = api.Overcloud(TEST_DATA.tuskarclient_overclouds.first())
        with patch('tuskar_ui.api.Overcloud', **{
            'spec_set': ['get', 'is_deployed'],
            'is_deployed': True,
            'get.return_value': oc,
        }) as Overcloud:
            res = self.client.get(INDEX_URL)
            request = Overcloud.get.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Overcloud.get.call_args_list,
                                 [call(request, 1)])

        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_create_get(self):
        res = self.client.get(CREATE_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/_fullscreen_workflow_base.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/undeployed_overview.html')
