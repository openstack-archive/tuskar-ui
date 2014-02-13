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

import contextlib

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
    'horizon:infrastructure:overcloud:detail', args=(1,))
TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)


class OvercloudTests(test.BaseAdminViewTests):

    def test_index_overcloud_undeployed_get(self):
        oc = None
        with patch('tuskar_ui.api.Overcloud', **{
            'spec_set': [
                'get',
                'is_deployed',
                'is_deploying',
                'is_failed',
                'stack',
            ],
            'stack': None,
            'is_deployed': False,
            'is_deploying': False,
            'is_failed': False,
            'get.side_effect': lambda request, overcloud_id: oc,
        }) as Overcloud:
            oc = api.Overcloud
            res = self.client.get(INDEX_URL)
            request = Overcloud.get.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Overcloud.get.call_args_list,
                                 [call(request, 1)])
        self.assertRedirectsNoFollow(res, CREATE_URL)

    def test_index_overcloud_deployed(self):
        oc = None
        stack = TEST_DATA.heatclient_stacks.first()
        with patch('tuskar_ui.api.Overcloud', **{
            'spec_set': [
                'get',
                'is_deployed',
                'is_deploying',
                'is_failed',
                'id',
                'stack',
            ],
            'stack': stack,
            'is_deployed': True,
            'is_deploying': False,
            'is_failed': False,
            'id': 1,
            'get.side_effect': lambda request, overcloud_id: oc,
        }) as Overcloud:
            oc = Overcloud
            res = self.client.get(INDEX_URL)
            request = Overcloud.get.call_args_list[0][0][0]  # This is a hack.
            self.assertListEqual(Overcloud.get.call_args_list,
                                 [call(request, 1)])

        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_create_get(self):
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        with contextlib.nested(patch('tuskar_ui.api.OvercloudRole', **{
            'spec_set': ['list'],
            'list.return_value': roles,
        }), patch('tuskar_ui.api.Node', **{
            'spec_set': ['list'],
            'list.return_value': [],
        })):
            res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/_fullscreen_workflow_base.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/undeployed_overview.html')

    def test_create_post(self):
        oc = None
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        data = {
            'count__1__': '1',
            'count__2__': '0',
            'count__3__': '0',
            'count__4__': '0',
        }
        with contextlib.nested(patch('tuskar_ui.api.OvercloudRole', **{
            'spec_set': ['list'],
            'list.return_value': roles,
        }), patch('tuskar_ui.api.Overcloud', **{
            'spec_set': ['create'],
            'create.return_value': oc,
        }), patch('tuskar_ui.api.Node', **{
            'spec_set': ['list'],
            'list.return_value': [],
        })) as (OvercloudRole, Overcloud, Node):
            oc = Overcloud
            res = self.client.post(CREATE_URL, data)
            request = Overcloud.create.call_args_list[0][0][0]
            self.assertListEqual(
                Overcloud.create.call_args_list,
                [
                    call(request, {
                        ('1', ''): 1,
                        ('2', ''): 0,
                        ('3', ''): 0,
                        ('4', ''): 0,
                    }),
                ])
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_detail_get(self):
        oc = None
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        with contextlib.nested(patch('tuskar_ui.api.Overcloud', **{
            'spec_set': [
                'get',
                'is_deployed',
                'is_deploying',
                'is_failed',
                'resources',
                'dashboard_url',
                'stack_events',
            ],
            'is_deployed': True,
            'is_deploying': False,
            'is_failed': False,
            'get.side_effect': lambda request, overcloud_id: oc,
            'resources.return_value': [],
            'dashboard_url': '',
            'stack_events': [],
        }), patch('tuskar_ui.api.OvercloudRole', **{
            'spec_set': ['list'],
            'list.return_value': roles,
        })) as (Overcloud, OvercloudRole):
            oc = Overcloud
            res = self.client.get(DETAIL_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/detail.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/_detail_overview.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/_detail_configuration.html')

    def test_role_edit_get(self):
        role = TEST_DATA.tuskarclient_overcloud_roles.first()
        url = urlresolvers.reverse(
            'horizon:infrastructure:overcloud:role_edit', args=(role.id,))
        with patch('tuskar_ui.api.OvercloudRole', **{
            'spec_set': ['get'],
            'get.return_value': role,
        }):
            res = self.client.get(url)
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/role_edit.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/_role_edit.html')

    def test_role_edit_post(self):
        role = TEST_DATA.tuskarclient_overcloud_roles.first()
        url = urlresolvers.reverse(
            'horizon:infrastructure:overcloud:role_edit', args=(role.id,))
        data = {
            'id': '1',
            'flavor_id': 'xxx',
        }
        with patch('tuskar_ui.api.OvercloudRole', **{
            'spec_set': ['get'],
            'get.return_value': role,
        }):
            # TODO(rdopieralski) Check if the role got associated with flavor.
            res = self.client.post(url, data)
        self.assertRedirectsNoFollow(res, CREATE_URL)
