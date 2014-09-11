# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import contextlib
import mock
from mock import patch, call  # noqa

from django.core import urlresolvers

from openstack_dashboard import api

from tuskar_ui.test import helpers as test

INDEX_URL = 'horizon:infrastructure:images:properties:index'
CREATE_URL = 'horizon:infrastructure:images:properties:create'
UPDATE_URL = 'horizon:infrastructure:images:properties:edit'


class ImageCustomPropertiesTests(test.BaseAdminViewTests):

    def test_list_properties(self):
        image = self.images.first()
        properties = []
        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get_properties',
                  return_value=properties),
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),) as (
                mock_image_get_properties, mock_image_get):
            res = self.client.get(
                urlresolvers.reverse(INDEX_URL, args=(image.id,)))

        self.assertEqual(res.status_code, 200)
        mock_image_get_properties.assert_called_once_with(
            mock.ANY, image.id, False)
        mock_image_get.assert_called_once_with(mock.ANY, image.id)
        self.assertTemplateUsed(
            res, 'infrastructure/images/properties/index.html')

    def test_property_create_get(self):
        image = self.images.first()
        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),) as (
                mock_image_get,):
            res = self.client.get(
                urlresolvers.reverse(CREATE_URL, args=(image.id,)))

        self.assertEqual(res.status_code, 200)
        mock_image_get.assert_called_once_with(mock.ANY, image.id)
        self.assertTemplateUsed(
            res, 'infrastructure/images/properties/create.html')

    def test_property_update_get(self):
        image = self.images.first()
        properties = []
        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get_property',
                  return_value=properties),
            patch('openstack_dashboard.api.glance.image_get',
                  return_value=image),) as (
                mock_image_get_properties, mock_image_get):
            res = self.client.get(
                urlresolvers.reverse(
                    UPDATE_URL, args=(image.id, 'property_key')))

        self.assertEqual(res.status_code, 200)
        mock_image_get_properties.assert_called_once_with(
            mock.ANY, image.id, 'property_key', False)
        mock_image_get.assert_called_once_with(mock.ANY, image.id)
        self.assertTemplateUsed(
            res, 'infrastructure/images/properties/edit.html')

    def test_property_create_post(self):
        image = self.images.list()[0]
        data = {'image_id': image.id,
                'key': 'k1',
                'value': 'v1'}

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_update_properties',
                  return_value=None),) as (mocked_create,):

            res = self.client.post(
                urlresolvers.reverse(CREATE_URL, args=(image.id,)), data)

        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(
            res, urlresolvers.reverse(INDEX_URL, args=(image.id,)))

        mocked_create.assert_called_once_with(
            mock.ANY, image.id, k1='v1')

    def test_property_update_post(self):
        image = self.images.list()[0]
        prop = api.glance.ImageCustomProperty(image.id, 'k1', 'v1')
        data = {'image_id': image.id,
                'key': 'k1',
                'value': 'v2'}

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get_property',
                  return_value=prop),
            patch('openstack_dashboard.api.glance.image_update_properties',
                  return_value=None),) as (mocked_get, mocked_update,):

            res = self.client.post(
                urlresolvers.reverse(UPDATE_URL,
                                     args=(image.id, prop.id)), data)

        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(
            res, urlresolvers.reverse(INDEX_URL, args=(image.id,)))

        mocked_get.assert_called_once_with(mock.ANY, image.id, prop.id, False)
        mocked_update.assert_called_once_with(
            mock.ANY, image.id, k1='v2')

    def test_property_delete_ok(self):
        image = self.images.list()[0]
        prop1 = api.glance.ImageCustomProperty(image.id, 'k1', 'v1')
        prop2 = api.glance.ImageCustomProperty(image.id, 'k2', 'v2')
        props = [prop1, prop2]

        data = {'action': 'properties__delete',
                'object_ids': [prop1.id, prop2.id]}

        with contextlib.nested(
            patch('openstack_dashboard.api.glance.image_get_properties',
                  return_value=props),
            patch('openstack_dashboard.api.glance.image_delete_properties',
                  return_value=None),) as (
                mock_prop_list, mock_prop_delete):

            res = self.client.post(
                urlresolvers.reverse(INDEX_URL, args=(image.id,)), data)

        mock_prop_delete.has_calls(
            call(mock.ANY, prop1.id),
            call(mock.ANY, prop2.id))
        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(
            res, urlresolvers.reverse(INDEX_URL, args=(image.id,)))
