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
import json
import mock
from mock import patch, call  # noqa

from django.core import urlresolvers

from openstack_dashboard.dashboards.project.images.images import forms

from tuskar_ui import api
from tuskar_ui.test import helpers as test

INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:images:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:images:create')
UPDATE_URL = 'horizon:infrastructure:images:update'
IMAGE_METADATA_URL = 'horizon:infrastructure:images:update_metadata'


class ImagesTest(test.BaseAdminViewTests):

    def test_index(self):
        roles = [api.tuskar.Role(role) for role in
                 self.tuskarclient_roles.list()]
        plans = [api.tuskar.Plan(plan) for plan in
                 self.tuskarclient_plans.list()]

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Role.list',
                  return_value=roles),
            patch('tuskar_ui.api.tuskar.Plan.list',
                  return_value=plans),
            patch('openstack_dashboard.api.glance.image_list_detailed',
                  return_value=[self.images.list(), False, False]),):

            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'infrastructure/images/index.html')

    def test_create_get(self):
        res = self.client.get(CREATE_URL)

        self.assertTemplateUsed(res, 'infrastructure/images/create.html')

    def test_update_get(self):
        image = self.images.list()[0]

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),) as (mocked_get,):

            res = self.client.get(
                urlresolvers.reverse(UPDATE_URL, args=(image.id,)))

        mocked_get.assert_called_once_with(mock.ANY, image.id)
        self.assertTemplateUsed(res, 'infrastructure/images/update.html')

    def test_create_post(self):
        image = self.images.list()[0]
        data = {
            'name': 'Fedora',
            'description': 'Login with admin/admin',
            'source_type': 'url',
            'copy_from': 'http://test_url.com',
            'disk_format': 'qcow2',
            'architecture': 'x86-64',
            'minimum_disk': 15,
            'minimum_ram': 512,
            'is_public': True,
            'protected': False}

        forms.IMAGE_FORMAT_CHOICES = [('qcow2', 'qcow2')]

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_create',
                  return_value=image),) as (mocked_create,):

            res = self.client.post(CREATE_URL, data)

        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        mocked_create.assert_called_once_with(
            mock.ANY, name=u'Fedora', container_format='bare', min_ram=512,
            disk_format=u'qcow2', copy_from=u'http://test_url.com',
            protected=False, min_disk=15, is_public=True,
            properties={'description': u'Login with admin/admin',
                        'architecture': u'x86-64'})

    def test_update_post(self):
        image = self.images.list()[0]
        data = {
            'image_id': image.id,
            'name': 'Fedora',
            'description': 'Login with admin/admin',
            'source_type': 'url',
            'copy_from': 'http://test_url.com',
            'disk_format': 'qcow2',
            'architecture': 'x86-64',
            'minimum_disk': 15,
            'minimum_ram': 512,
            'is_public': True,
            'protected': False}

        forms.IMAGE_FORMAT_CHOICES = [('qcow2', 'qcow2')]

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),
            patch('openstack_dashboard.api.glance.image_update',
                  return_value=image),) as (mocked_get, mocked_update,):

            res = self.client.post(
                urlresolvers.reverse(UPDATE_URL, args=(image.id,)), data)

        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        mocked_get.assert_called_once_with(mock.ANY, image.id)
        mocked_update.assert_called_once_with(
            mock.ANY, image.id, name='Fedora', container_format='bare',
            min_ram=512, disk_format='qcow2', protected=False,
            is_public=False, min_disk=15, purge_props=False,
            properties={'description': 'Login with admin/admin',
                        'architecture': 'x86-64'})

    def test_delete_ok(self):
        roles = [api.tuskar.Role(role) for role in
                 self.tuskarclient_roles.list()]
        plans = [api.tuskar.Plan(plan) for plan in
                 self.tuskarclient_plans.list()]
        images = self.images.list()

        data = {'action': 'images__delete',
                'object_ids': [images[0].id, images[1].id]}

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Role.list',
                  return_value=roles),
            patch('tuskar_ui.api.tuskar.Plan.list',
                  return_value=plans),
            patch('openstack_dashboard.api.glance.image_list_detailed',
                  return_value=[images, False, False]),
            patch('openstack_dashboard.api.glance.image_delete',
                  return_value=None),) as (
                mock_role_list, plan_list, mock_image_lict, mock_image_delete):

            res = self.client.post(INDEX_URL, data)

        mock_image_delete.has_calls(
            call(mock.ANY, images[0].id),
            call(mock.ANY, images[1].id))
        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_images_metadata_get(self):
        image = self.images.first()
        namespaces = self.metadata_defs.list()

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),
            patch('openstack_dashboard.api.glance.metadefs_namespace_list',
                  return_value=(namespaces, False, False)),
            patch('openstack_dashboard.api.glance.metadefs_namespace_get',
                  return_value=namespaces[0]),) as (
                mocked_get, mocked_namespaces_list, mocked_namespace_get,):

            res = self.client.get(
                urlresolvers.reverse(IMAGE_METADATA_URL, args=(image.id,)))

        mocked_get.assert_called_once_with(mock.ANY, image.id)
        mocked_namespaces_list.assert_called_once_with(
            mock.ANY, filters={'resource_types': ['OS::Glance::Image']})

        self.assertEqual(mocked_namespace_get.call_count, 4)

        self.assertTemplateUsed(
            res, 'infrastructure/images/update_metadata.html')

    def test_images_metadata_update(self):
        image = self.images.first()

        metadata = [{"value": "mock_value", "key": "hw_machine_type"}]
        formData = {"metadata": json.dumps(metadata)}

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),
            patch('openstack_dashboard.api.glance.image_update_properties',
                  return_value=None),) as (

                mocked_get, mocked_update,):

            res = self.client.post(
                urlresolvers.reverse(IMAGE_METADATA_URL, args=(image.id,)),
                formData)

        mocked_get.assert_called_once_with(mock.ANY, image.id)
        mocked_update.assert_called_once_with(
            mock.ANY,  image.id, ['image_type'], hw_machine_type='mock_value')

        self.assertEqual(res.status_code, 302)
        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)
