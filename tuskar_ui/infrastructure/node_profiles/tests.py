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

from novaclient.v1_1 import servers

from horizon import exceptions
from openstack_dashboard.test.test_data import utils
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import tuskar_data


TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)
INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:node_profiles:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:node_profiles:create')


@contextlib.contextmanager
def _prepare_create():
    flavor = TEST_DATA.novaclient_flavors.first()
    all_flavors = TEST_DATA.novaclient_flavors.list()
    images = TEST_DATA.glanceclient_images.list()
    data = {'name': 'foobar',
            'vcpus': 3,
            'memory_mb': 1024,
            'disk_gb': 40,
            'arch': 'amd64',
            'kernel_image_id': images[0].id,
            'ramdisk_image_id': images[1].id}
    with contextlib.nested(
            patch('tuskar_ui.api.NodeProfile.create',
                  return_value=flavor),
            patch('openstack_dashboard.api.glance.image_list_detailed',
                  return_value=(TEST_DATA.glanceclient_images.list(), False)),
            # Inherited code calls this directly
            patch('openstack_dashboard.api.nova.flavor_list',
                  return_value=all_flavors),
    ) as mocks:
            yield mocks[0], data


class NodeProfilesTest(test.BaseAdminViewTests):

    def test_index(self):
        with contextlib.nested(
                patch('openstack_dashboard.api.nova.flavor_list',
                      return_value=TEST_DATA.novaclient_flavors.list()),
                patch('openstack_dashboard.api.nova.server_list',
                      return_value=([], False)),
        ) as (flavors_mock, servers_mock):
            res = self.client.get(INDEX_URL)
            self.assertEqual(flavors_mock.call_count, 1)
            self.assertEqual(servers_mock.call_count, 1)

        self.assertTemplateUsed(res,
                                'infrastructure/node_profiles/index.html')

    def test_index_recoverable_failure(self):
        with patch('openstack_dashboard.api.nova.flavor_list',
                   side_effect=exceptions.Conflict):
            self.client.get(INDEX_URL)
            # FIXME(dtantsur): I expected the following to work:
            # self.assertMessageCount(error=1, warning=0)

    def test_create_get(self):
        with patch('openstack_dashboard.api.glance.image_list_detailed',
                   return_value=([], False)) as mock:
            res = self.client.get(CREATE_URL)
            self.assertEqual(mock.call_count, 2)
        self.assertTemplateUsed(res,
                                'infrastructure/node_profiles/create.html')

    def test_create_get_recoverable_failure(self):
        with patch('openstack_dashboard.api.glance.image_list_detailed',
                   side_effect=exceptions.Conflict):
            self.client.get(CREATE_URL)
            self.assertMessageCount(error=1, warning=0)

    def test_create_post_ok(self):
        images = TEST_DATA.glanceclient_images.list()
        with _prepare_create() as (create_mock, data):
            res = self.client.post(CREATE_URL, data)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            request = create_mock.call_args_list[0][0][0]
            self.assertListEqual(create_mock.call_args_list, [
                call(request, name=u'foobar', memory=1024, vcpus=3, disk=40,
                     cpu_arch='amd64', kernel_image_id=images[0].id,
                     ramdisk_image_id=images[1].id)
            ])

    def test_create_post_name_exists(self):
        flavor = TEST_DATA.novaclient_flavors.first()
        with _prepare_create() as (create_mock, data):
            data['name'] = flavor.name
            res = self.client.post(CREATE_URL, data)
            self.assertFormErrors(res)

    def test_delete_ok(self):
        flavors = TEST_DATA.novaclient_flavors.list()
        data = {'action': 'node_profiles__delete',
                'object_ids': [flavors[0].id, flavors[1].id]}
        with contextlib.nested(
                patch('openstack_dashboard.api.nova.flavor_delete'),
                patch('openstack_dashboard.api.nova.server_list',
                      return_value=([], False)),
                patch('openstack_dashboard.api.glance.image_list_detailed',
                      return_value=([], False)),
                patch('openstack_dashboard.api.nova.flavor_list',
                      return_value=TEST_DATA.novaclient_flavors.list())
        ) as (delete_mock, server_list_mock, glance_mock, flavors_mock):
            res = self.client.post(INDEX_URL, data)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            self.assertEqual(delete_mock.call_count, 2)
            self.assertEqual(server_list_mock.call_count, 1)

    def test_delete_deployed(self):
        flavors = TEST_DATA.novaclient_flavors.list()
        server = servers.Server(
            servers.ServerManager(None),
            {'id': 'aa',
             'name': 'Compute',
             'image': {'id': 1},
             'status': 'ACTIVE',
             'flavor': {'id': flavors[0].id}}
        )
        data = {'action': 'node_profiles__delete',
                'object_ids': [flavors[0].id, flavors[1].id]}
        with contextlib.nested(
                patch('openstack_dashboard.api.nova.flavor_delete'),
                patch('openstack_dashboard.api.nova.server_list',
                      return_value=([server], False)),
                patch('openstack_dashboard.api.glance.image_list_detailed',
                      return_value=([], False)),
                patch('openstack_dashboard.api.nova.flavor_list',
                      return_value=TEST_DATA.novaclient_flavors.list())
        ) as (delete_mock, server_list_mock, glance_mock, flavors_mock):
            res = self.client.post(INDEX_URL, data)
            self.assertMessageCount(error=1, warning=0)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            self.assertEqual(delete_mock.call_count, 1)
            self.assertEqual(server_list_mock.call_count, 1)
