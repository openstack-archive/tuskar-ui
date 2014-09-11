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

import mock
from mock import patch  # noqa

from tuskar_ui import api
from tuskar_ui.test import helpers as test

INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:images:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:infrastructure:images:create')
UPDATE_URL = 'horizon:infrastructure:images:update'


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
            res = self.client.post(
                urlresolvers.reverse(UPDATE_URL, args=(image.id,)))

        mocked_get.assert_called_once_with(mock.ANY, image.id)
        self.assertTemplateUsed(res, 'infrastructure/images/update.html')

    def test_create_post(self):
        #TODO(lsmola) can be tested once Tuskar ui is merged into Horizon
        pass

    def test_update_put(self):
        #TODO(lsmola) can be tested once Tuskar ui is merged into Horizon
        pass
