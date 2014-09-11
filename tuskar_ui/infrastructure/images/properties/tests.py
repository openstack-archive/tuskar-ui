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

from django.core import urlresolvers

import mock
from mock import patch  # noqa

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

    #@test.create_stubs({api.glance: ('image_get',
    #                                 'image_get_property'), })
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
        #TODO(lsmola) can be tested once Tuskar ui is merged into Horizon
        pass

    def test_property_update_post(self):
        #TODO(lsmola) can be tested once Tuskar ui is merged into Horizon
        pass
