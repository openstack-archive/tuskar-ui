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
    images = TEST_DATA.glanceclient_images.list()
    data = {'name': 'foobar',
            'vcpus': 3,
            'memory_mb': 1024,
            'disk_gb': 40,
            'arch': 'amd64',
            'kernel_id': images[0].id,
            'ramdisk_id': images[1].id}
    with patch('openstack_dashboard.api.nova', **{
            'spec_set': ['flavor_create', 'flavor_list', 'flavor_get_extras',
                         'flavor_extra_set'],
            'flavor_create.return_value': flavor,
            'flavor_list.return_value': TEST_DATA.novaclient_flavors.list(),
            'flavor_get_extras.return_value': {},
    }) as nova_mock:
        with patch('openstack_dashboard.api.glance', **{
                'spec_set': ['image_list_detailed'],
                'image_list_detailed.return_value':
                (TEST_DATA.glanceclient_images.list(), False)
        }) as glance_mock:
            yield nova_mock, glance_mock, data


class NodeProfilesTest(test.BaseAdminViewTests):

    def test_index(self):
        with patch('openstack_dashboard.api.nova', **{
                'spec_set': ['flavor_list'],
                'flavor_list.return_value':
                TEST_DATA.novaclient_flavors.list(),
        }) as mock:
            res = self.client.get(INDEX_URL)
            self.assertEqual(mock.flavor_list.call_count, 1)

        self.assertTemplateUsed(res,
                                'infrastructure/node_profiles/index.html')

    def test_create_get(self):
        with patch('openstack_dashboard.api.glance', **{
                'spec_set': ['image_list_detailed'],
                'image_list_detailed.return_value': ([], False)
        }):
            res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(res,
                                'infrastructure/node_profiles/create.html')

    def test_create_post_ok(self):
        flavor = TEST_DATA.novaclient_flavors.first()
        images = TEST_DATA.glanceclient_images.list()
        with _prepare_create() as (nova_mock, glance_mock, data):
            res = self.client.post(CREATE_URL, data)
            self.assertNoFormErrors(res)
            self.assertRedirectsNoFollow(res, INDEX_URL)
            request = nova_mock.flavor_create.call_args_list[0][0][0]
            self.assertListEqual(nova_mock.flavor_create.call_args_list, [
                call(request, name=u'foobar', memory=1024, vcpu=3, disk=40,
                     flavorid='auto', ephemeral=0, swap=0, is_public=True)
            ])
            self.assertEqual(nova_mock.flavor_list.call_count, 1)
            expected_extras = {'cpu_arch': 'amd64',
                               'baremetal:deploy_kernel_id': images[0].id,
                               'baremetal:deploy_ramdisk_id': images[1].id}
            self.assertListEqual(nova_mock.flavor_extra_set.call_args_list, [
                call(request, flavor.id, expected_extras),
            ])

    def test_create_post_name_exists(self):
        flavor = TEST_DATA.novaclient_flavors.first()
        with _prepare_create() as (nova_mock, glance_mock, data):
            data['name'] = flavor.name
            res = self.client.post(CREATE_URL, data)
            self.assertFormErrors(res)
