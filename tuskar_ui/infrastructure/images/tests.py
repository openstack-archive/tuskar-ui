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

from tuskar_ui import api
from tuskar_ui.test import helpers as test

INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:images:index')


class ImagesTest(test.BaseAdminViewTests):

    def test_index(self):
        roles = [api.tuskar.OvercloudRole(role) for role in
                 self.tuskarclient_roles.list()]
        plans = [api.tuskar.OvercloudPlan(plan) for plan in
                 self.tuskarclient_plans.list()]

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.OvercloudRole.list',
                  return_value=roles),
            patch('tuskar_ui.api.tuskar.OvercloudPlan.list',
                  return_value=plans),
            patch('openstack_dashboard.api.glance.image_list_detailed',
                  return_value=[self.images.list(), False, False]),):
            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'infrastructure/images/index.html')
