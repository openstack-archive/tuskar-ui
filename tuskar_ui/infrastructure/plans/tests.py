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
from tuskar_ui.test.test_data import flavor_data
from tuskar_ui.test.test_data import heat_data
from tuskar_ui.test.test_data import node_data
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:plans:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:plans:create')
OVERCLOUD_INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:index')

TEST_DATA = utils.TestDataContainer()
flavor_data.data(TEST_DATA)
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)


class OvercloudTests(test.BaseAdminViewTests):

    def test_index_no_plan_get(self):
        with contextlib.nested(
                patch('tuskar_ui.api.tuskar.OvercloudPlan.get_the_plan',
                      return_value=None),
        ):
            res = self.client.get(INDEX_URL)
        self.assertRedirectsNoFollow(res, CREATE_URL)

    def test_index_with_plan_get(self):
        plan = api.tuskar.OvercloudPlan(TEST_DATA.tuskarclient_plans.first())
        with contextlib.nested(
                patch('tuskar_ui.api.tuskar.OvercloudPlan.get_the_plan',
                      return_value=plan),
        ):
            res = self.client.get(INDEX_URL)
            request = api.tuskar.OvercloudPlan.get_the_plan. \
                call_args_list[0][0][0]
            self.assertListEqual(
                api.tuskar.OvercloudPlan.get_the_plan.call_args_list,
                [call(request)])
        self.assertRedirectsNoFollow(res, OVERCLOUD_INDEX_URL)

    # TODO(tzumainn): these tests need to be completely redone
    # def test_scale_get(self):
    #     oc = None
    #     roles = [api.tuskar.OvercloudRole(role)
    #              for role in TEST_DATA.tuskarclient_roles.list()]
    #     with contextlib.nested(
    #         patch('tuskar_ui.api.tuskar.OvercloudRole', **{
    #             'spec_set': ['list'],
    #             'list.return_value': roles,
    #         }),
    #         _mock_plan(counts=[{
    #             "overcloud_role_id": role['id'],
    #             "num_nodes": 0,
    #         } for role in roles]),
    #         patch('openstack_dashboard.api.nova', **{
    #             'spec_set': ['flavor_list'],
    #             'flavor_list.return_value': [],
    #         }),
    #     ) as (OvercloudRole, Overcloud, nova):
    #         oc = Overcloud
    #         url = urlresolvers.reverse(
    #             'horizon:infrastructure:overcloud:scale', args=(oc.id,))
    #         res = self.client.get(url)
    #     self.assertTemplateUsed(
    #         res, 'infrastructure/overcloud/scale_node_counts.html')

    # def test_scale_post(self):
    #     node = TEST_DATA.ironicclient_nodes.first
    #     roles = [api.tuskar.OvercloudRole(role)
    #              for role in TEST_DATA.tuskarclient_roles.list()]
    #     flavor = TEST_DATA.novaclient_flavors.first()
    #     old_flavor_id = roles[0].flavor_id
    #     roles[0].flavor_id = flavor.id
    #     data = {
    #         'plan_id': '1',
    #         'count__1__%s' % flavor.id: '1',
    #         'count__2__': '0',
    #         'count__3__': '0',
    #         'count__4__': '0',
    #     }
    #     with contextlib.nested(
    #         patch('tuskar_ui.api.tuskar.OvercloudRole', **{
    #             'spec_set': ['list'],
    #             'list.return_value': roles,
    #         }),
    #         _mock_plan(counts=[{
    #             "overcloud_role_id": role['id'],
    #             "num_nodes": 0,
    #         } for role in roles]),
    #         patch('tuskar_ui.api.node.Node', **{
    #             'spec_set': ['list'],
    #             'list.return_value': [node],
    #         }),
    #         patch('openstack_dashboard.api.nova', **{
    #             'spec_set': ['flavor_list'],
    #             'flavor_list.return_value': [flavor],
    #         }),
    #     ) as (OvercloudRole, Overcloud, Node, nova):
    #         url = urlresolvers.reverse(
    #             'horizon:infrastructure:overcloud:scale',
    #             args=(Overcloud.id,))
    #         res = self.client.post(url, data)

    #         request = Overcloud.update.call_args_list[0][0][0]
    #         self.assertListEqual(
    #             Overcloud.update.call_args_list,
    #             [
    #                 call(request, Overcloud.id, {
    #                     ('1', flavor.id): 1,
    #                     ('2', ''): 0,
    #                     ('3', ''): 0,
    #                     ('4', ''): 0,
    #                 }, {}),
    #             ])
    #     roles[0].flavor_id = old_flavor_id
    #     self.assertRedirectsNoFollow(res, DETAIL_URL)
