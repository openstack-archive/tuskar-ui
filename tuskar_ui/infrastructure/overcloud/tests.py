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

import collections
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
    'horizon:infrastructure:overcloud:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:create')
DETAIL_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:detail', args=(1,))
UNDEPLOY_IN_PROGRESS_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:undeploy_in_progress',
    args=('overcloud',))
UNDEPLOY_IN_PROGRESS_URL_LOG_TAB = (
    UNDEPLOY_IN_PROGRESS_URL + "?tab=undeploy_in_progress__log")
DETAIL_URL_CONFIGURATION_TAB = (DETAIL_URL +
                                "?tab=detail__configuration")
DETAIL_URL_LOG_TAB = (DETAIL_URL + "?tab=detail__log")
DELETE_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:undeploy_confirmation', args=(1,))
TEST_DATA = utils.TestDataContainer()
flavor_data.data(TEST_DATA)
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)
tuskar_data.data(TEST_DATA)


@contextlib.contextmanager
def _mock_plan(**kwargs):
    plan = None
    stack = api.heat.Stack(TEST_DATA.heatclient_stacks.first())
    stack.events = []
    stack.resources_by_role = lambda *args, **kwargs: []
    stack.resources = lambda *args, **kwargs: []
    stack.overcloud_keystone = None
    template_parameters = {
        "NeutronPublicInterfaceRawDevice": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("If set, the public interface is a vlan with this "
                            "device as the raw device."),
        },
        "HeatPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the Heat service account, used "
                            "by the Heat services.")
        },
    }

    params = {
        'spec_set': [
            'counts',
            'create',
            'delete',
            'get',
            'get_the_plan',
            'id',
            'stack',
            'update',
            'template_parameters',
        ],
        'counts': [],
        'create.side_effect': lambda *args, **kwargs: plan,
        'delete.return_value': None,
        'get.side_effect': lambda *args, **kwargs: plan,
        'get_the_plan.side_effect': lambda *args, **kwargs: plan,
        'id': 1,
        'stack': stack,
        'update.side_effect': lambda *args, **kwargs: plan,
        'template_parameters.return_value': template_parameters,
    }
    params.update(kwargs)
    with patch(
            'tuskar_ui.api.tuskar.OvercloudPlan', **params) as OvercloudPlan:
        plan = OvercloudPlan
        yield OvercloudPlan


class OvercloudTests(test.BaseAdminViewTests):

    def test_index_overcloud_undeployed_get(self):
        with _mock_plan(**{'get_the_plan.side_effect': None,
                           'get_the_plan.return_value': None}):
            res = self.client.get(INDEX_URL)

        self.assertRedirectsNoFollow(res, CREATE_URL)

    def test_index_overcloud_deployed_stack_not_created(self):
        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.is_deployed',
                      return_value=False),
        ):
            res = self.client.get(INDEX_URL)
            request = api.tuskar.OvercloudPlan.get_the_plan. \
                call_args_list[0][0][0]
            self.assertListEqual(
                api.tuskar.OvercloudPlan.get_the_plan.call_args_list,
                [call(request)])
        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_index_overcloud_deployed(self):
        with _mock_plan() as OvercloudPlan:
            res = self.client.get(INDEX_URL)
            request = OvercloudPlan.get_the_plan.call_args_list[0][0][0]
            self.assertListEqual(OvercloudPlan.get_the_plan.call_args_list,
                                 [call(request)])

        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_detail_get(self):
        roles = [api.tuskar.OvercloudRole(role)
                 for role in TEST_DATA.tuskarclient_roles.list()]

        with contextlib.nested(
            _mock_plan(),
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
        ) as (Overcloud, OvercloudRole):
            res = self.client.get(DETAIL_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/detail.html')
        self.assertTemplateNotUsed(
            res, 'horizon/common/_detail_table.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/_detail_overview.html')

    def test_detail_get_configuration_tab(self):
        with _mock_plan():
            res = self.client.get(DETAIL_URL_CONFIGURATION_TAB)

        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/detail.html')
        self.assertTemplateNotUsed(
            res, 'infrastructure/overcloud/_detail_overview.html')
        self.assertTemplateUsed(
            res, 'horizon/common/_detail_table.html')

    def test_detail_get_log_tab(self):
        with _mock_plan():
            res = self.client.get(DETAIL_URL_LOG_TAB)

        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/detail.html')
        self.assertTemplateNotUsed(
            res, 'infrastructure/overcloud/_detail_overview.html')
        self.assertTemplateUsed(
            res, 'horizon/common/_detail_table.html')

    def test_delete_get(self):
        res = self.client.get(DELETE_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/undeploy_confirmation.html')

    def test_delete_post(self):
        with _mock_plan():
            res = self.client.post(DELETE_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_undeploy_in_progress(self):
        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.is_deleting',
                      return_value=True),
                patch('tuskar_ui.api.heat.Stack.is_deployed',
                      return_value=False),
        ):
            res = self.client.get(UNDEPLOY_IN_PROGRESS_URL)

        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/detail.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/_undeploy_in_progress.html')
        self.assertTemplateNotUsed(
            res, 'horizon/common/_detail_table.html')

    def test_undeploy_in_progress_finished(self):
        with _mock_plan(**{'get_the_plan.side_effect': None,
                           'get_the_plan.return_value': None}):
            res = self.client.get(UNDEPLOY_IN_PROGRESS_URL)

        self.assertRedirectsNoFollow(res, CREATE_URL)

    def test_undeploy_in_progress_invalid(self):
        with _mock_plan():
            res = self.client.get(UNDEPLOY_IN_PROGRESS_URL)

        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_undeploy_in_progress_log_tab(self):
        with contextlib.nested(
                _mock_plan(),
                patch('tuskar_ui.api.heat.Stack.is_deleting',
                      return_value=True),
                patch('tuskar_ui.api.heat.Stack.is_deployed',
                      return_value=False),
        ):
            res = self.client.get(UNDEPLOY_IN_PROGRESS_URL_LOG_TAB)

        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/detail.html')
        self.assertTemplateNotUsed(
            res, 'infrastructure/overcloud/_undeploy_in_progress.html')
        self.assertTemplateUsed(
            res, 'horizon/common/_detail_table.html')

    def test_scale_get(self):
        oc = None
        roles = [api.tuskar.OvercloudRole(role)
                 for role in TEST_DATA.tuskarclient_roles.list()]
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            _mock_plan(counts=[{
                "overcloud_role_id": role['id'],
                "num_nodes": 0,
            } for role in roles]),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [],
            }),
        ) as (OvercloudRole, Overcloud, nova):
            oc = Overcloud
            url = urlresolvers.reverse(
                'horizon:infrastructure:overcloud:scale', args=(oc.id,))
            res = self.client.get(url)
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/scale_node_counts.html')

    def test_scale_post(self):
        node = TEST_DATA.ironicclient_nodes.first
        roles = [api.tuskar.OvercloudRole(role)
                 for role in TEST_DATA.tuskarclient_roles.list()]
        flavor = TEST_DATA.novaclient_flavors.first()
        old_flavor_id = roles[0].flavor_id
        roles[0].flavor_id = flavor.id
        data = {
            'plan_id': '1',
            'count__1__%s' % flavor.id: '1',
            'count__2__': '0',
            'count__3__': '0',
            'count__4__': '0',
        }
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            _mock_plan(counts=[{
                "overcloud_role_id": role['id'],
                "num_nodes": 0,
            } for role in roles]),
            patch('tuskar_ui.api.node.Node', **{
                'spec_set': ['list'],
                'list.return_value': [node],
            }),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [flavor],
            }),
        ) as (OvercloudRole, Overcloud, Node, nova):
            url = urlresolvers.reverse(
                'horizon:infrastructure:overcloud:scale', args=(Overcloud.id,))
            res = self.client.post(url, data)

            request = Overcloud.update.call_args_list[0][0][0]
            self.assertListEqual(
                Overcloud.update.call_args_list,
                [
                    call(request, Overcloud.id, {
                        ('1', flavor.id): 1,
                        ('2', ''): 0,
                        ('3', ''): 0,
                        ('4', ''): 0,
                    }, {}),
                ])
        roles[0].flavor_id = old_flavor_id
        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_role_edit_get(self):
        role = api.tuskar.OvercloudRole(TEST_DATA.tuskarclient_roles.first())
        url = urlresolvers.reverse(
            'horizon:infrastructure:overcloud:role_edit', args=(role['id'],))
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': ['get'],
                'get.return_value': role,
            }),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [],
            }),
        ):
            res = self.client.get(url)
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/role_edit.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/_role_edit.html')

    def test_role_edit_post(self):
        role = None
        Flavor = collections.namedtuple('Flavor', 'id name')
        flavor = Flavor('xxx', 'Xxx')
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.OvercloudRole', **{
                'spec_set': [
                    'get',
                    'update',
                    'id',
                    'name',
                    'description',
                    'image_name',
                    'flavor_id',
                ],
                'get.side_effect': lambda *args, **kwargs: role,
                'name': 'Compute',
                'description': '...',
                'image_name': '',
                'id': 1,
                'flavor_id': '',
            }),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [flavor],
            }),
        ) as (OvercloudRole, nova):
            role = OvercloudRole
            url = urlresolvers.reverse(
                'horizon:infrastructure:overcloud:role_edit', args=(role.id,))
            data = {
                'id': str(role.id),
                'flavor_id': flavor.id,
            }
            res = self.client.post(url, data)
            request = OvercloudRole.update.call_args_list[0][0][0]
            self.assertListEqual(
                OvercloudRole.update.call_args_list,
                [call(request, flavor_id=flavor.id)])
        self.assertRedirectsNoFollow(res, CREATE_URL)
