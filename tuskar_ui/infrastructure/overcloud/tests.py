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
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:create')
DETAIL_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:detail', args=(1,))
DETAIL_URL_CONFIGURATION_TAB = (DETAIL_URL +
                                "?tab=detail__configuration")
DETAIL_URL_LOG_TAB = (DETAIL_URL + "?tab=detail__log")
DELETE_URL = urlresolvers.reverse(
    'horizon:infrastructure:overcloud:undeploy_confirmation', args=(1,))
TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)


@contextlib.contextmanager
def _mock_overcloud(**kwargs):
    oc = None
    stack = TEST_DATA.heatclient_stacks.first()
    params = {
        'spec_set': [
            'counts',
            'create',
            'dashboard_url',
            'delete',
            'get',
            'get_the_overcloud',
            'id',
            'is_deployed',
            'is_deploying',
            'is_failed',
            'resources',
            'stack',
            'stack_events',
            'update',
        ],
        'counts': [],
        'create.side_effect': lambda *args, **kwargs: oc,
        'dashboard_url': '',
        'delete.return_value': None,
        'get.side_effect': lambda *args, **kwargs: oc,
        'get_the_overcloud.side_effect': lambda *args, **kwargs: oc,
        'id': 1,
        'is_deployed': True,
        'is_deploying': False,
        'is_failed': False,
        'resources.return_value': [],
        'stack_events': [],
        'stack': stack,
        'update.side_effect': lambda *args, **kwargs: oc,
    }
    params.update(kwargs)
    with patch('tuskar_ui.api.Overcloud', **params) as Overcloud:
        oc = Overcloud
        yield Overcloud


class OvercloudTests(test.BaseAdminViewTests):

    def test_index_overcloud_undeployed_get(self):
        with patch('tuskar_ui.api.Overcloud.list', return_value=[]):
            res = self.client.get(INDEX_URL)

        self.assertRedirectsNoFollow(res, CREATE_URL)

    def test_index_overcloud_deployed_stack_not_created(self):
        with _mock_overcloud(is_deployed=False, stack=None) as Overcloud:
            res = self.client.get(INDEX_URL)
            request = Overcloud.get_the_overcloud.call_args_list[0][0][0]
            self.assertListEqual(Overcloud.get_the_overcloud.call_args_list,
                                 [call(request)])
        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_index_overcloud_deployed(self):
        with _mock_overcloud() as Overcloud:
            res = self.client.get(INDEX_URL)
            request = Overcloud.get_the_overcloud.call_args_list[0][0][0]
            self.assertListEqual(Overcloud.get_the_overcloud.call_args_list,
                                 [call(request)])

        self.assertRedirectsNoFollow(res, DETAIL_URL)

    def test_create_get(self):
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        with contextlib.nested(
            patch('tuskar_ui.api.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            patch('tuskar_ui.api.Node', **{
                'spec_set': ['list'],
                'list.return_value': [],
            }),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [],
            }),
        ):
            res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(
            res, 'infrastructure/_fullscreen_workflow_base.html')
        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/undeployed_overview.html')

    def test_create_post(self):
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        flavor = TEST_DATA.novaclient_flavors.first()
        old_flavor_id = roles[0].flavor_id
        roles[0].flavor_id = flavor.id
        data = {
            'count__1__%s' % flavor.id: '1',
            'count__2__': '0',
            'count__3__': '0',
            'count__4__': '0',
        }
        with contextlib.nested(
            patch('tuskar_ui.api.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            _mock_overcloud(),
            patch('tuskar_ui.api.Node', **{
                'spec_set': ['list'],
                'list.return_value': [],
            }),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [flavor],
            }),
        ) as (OvercloudRole, Overcloud, Node, nova):
            res = self.client.post(CREATE_URL, data)
            request = Overcloud.create.call_args_list[0][0][0]
            self.assertListEqual(
                Overcloud.create.call_args_list,
                [
                    call(request, {
                        ('1', flavor.id): 1,
                        ('2', ''): 0,
                        ('3', ''): 0,
                        ('4', ''): 0,
                    }, {
                        'NeutronPublicInterfaceRawDevice': '',
                        'NovaComputeDriver': '',
                        'NeutronPassword': '',
                        'NeutronFlatNetworks': '',
                        'NeutronPublicInterfaceDefaultRoute': '',
                        'HeatPassword': '',
                        'notcomputeImage': '',
                        'NovaImage': '',
                        'SSLKey': '',
                        'KeyName': '',
                        'GlancePassword': '',
                        'CeilometerPassword': '',
                        'NtpServer': '',
                        'CinderPassword': '',
                        'ImageUpdatePolicy': '',
                        'NeutronPublicInterface': '',
                        'NovaPassword': '',
                        'AdminToken': '',
                        'SwiftHashSuffix': '',
                        'NeutronPublicInterfaceIP': '',
                        'NovaComputeLibvirtType': '',
                        'AdminPassword': '',
                        'CeilometerComputeAgent': '',
                        'NeutronBridgeMappings': '',
                        'SwiftPassword': '',
                        'CeilometerMeteringSecret': '',
                        'SSLCertificate': '',
                        'Flavor': '',
                    }),
                ])
        roles[0].flavor_id = old_flavor_id
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_create_post_invalid_flavor(self):
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        old_flavor_id = roles[0].flavor_id
        roles[0].flavor_id = 'non-existing'
        data = {
            'count__1__%s' % roles[0].flavor_id: '1',
            'count__2__': '0',
            'count__3__': '0',
            'count__4__': '0',
        }
        with contextlib.nested(
            patch('tuskar_ui.api.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            _mock_overcloud(),
            patch('tuskar_ui.api.Node', **{
                'spec_set': ['list'],
                'list.return_value': [],
            }),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [],
            }),
        ) as (OvercloudRole, Overcloud, Node, nova):
            res = self.client.post(CREATE_URL, data)
            self.assertFormErrors(res)
        roles[0].flavor_id = old_flavor_id

    def test_detail_get(self):
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        with contextlib.nested(
            _mock_overcloud(),
            patch('tuskar_ui.api.OvercloudRole', **{
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
        with _mock_overcloud():
            res = self.client.get(DETAIL_URL_CONFIGURATION_TAB)

        self.assertTemplateUsed(
            res, 'infrastructure/overcloud/detail.html')
        self.assertTemplateNotUsed(
            res, 'infrastructure/overcloud/_detail_overview.html')
        self.assertTemplateUsed(
            res, 'horizon/common/_detail_table.html')

    def test_detail_get_log_tab(self):
        with _mock_overcloud():
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
        with _mock_overcloud():
            res = self.client.post(DELETE_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_scale_get(self):
        oc = None
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        with contextlib.nested(
            patch('tuskar_ui.api.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            _mock_overcloud(counts=[{
                "overcloud_role_id": role.id,
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
        roles = TEST_DATA.tuskarclient_overcloud_roles.list()
        flavor = TEST_DATA.novaclient_flavors.first()
        old_flavor_id = roles[0].flavor_id
        roles[0].flavor_id = flavor.id
        data = {
            'overcloud_id': '1',
            'count__1__%s' % flavor.id: '1',
            'count__2__': '0',
            'count__3__': '0',
            'count__4__': '0',
        }
        with contextlib.nested(
            patch('tuskar_ui.api.OvercloudRole', **{
                'spec_set': ['list'],
                'list.return_value': roles,
            }),
            _mock_overcloud(counts=[{
                "overcloud_role_id": role.id,
                "num_nodes": 0,
            } for role in roles]),
            patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value': [flavor],
            }),
        ) as (OvercloudRole, Overcloud, nova):
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
        role = TEST_DATA.tuskarclient_overcloud_roles.first()
        url = urlresolvers.reverse(
            'horizon:infrastructure:overcloud:role_edit', args=(role.id,))
        with contextlib.nested(
            patch('tuskar_ui.api.OvercloudRole', **{
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
            patch('tuskar_ui.api.OvercloudRole', **{
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
