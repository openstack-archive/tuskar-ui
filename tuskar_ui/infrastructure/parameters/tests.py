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
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:parameters:index')
SERVICE_CONFIG_URL = urlresolvers.reverse(
    'horizon:infrastructure:parameters:service_configuration')

TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)

from tuskar_ui.infrastructure.parameters import views


class ParametersTest(test.BaseAdminViewTests):

    def test_index(self):
        plans = [api.tuskar.Plan(plan)
                 for plan in self.tuskarclient_plans.list()]
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]

        with contextlib.nested(
                patch('tuskar_ui.api.tuskar.Plan.list',
                      return_value=plans),
                patch('tuskar_ui.api.tuskar.Role.list',
                      return_value=roles),
        ):
            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'infrastructure/parameters/index.html')

    def test_param_object(self):
        param_dict = {'parameter_group': 'Neutron',
                      'value': '1.2.3.4',
                      'name': 'Ip Address',
                      'description': 'This is an IP Address'}

        p = views.ServiceParameter(param_dict, 5)
        self.assertEqual(p.id, 5)
        self.assertEqual(p.value, '1.2.3.4')

    def test_service_config_get(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        role = api.tuskar.Role(self.tuskarclient_roles.first())
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.get_role_by_name',
                  return_value=role),
        ):
            res = self.client.get(SERVICE_CONFIG_URL)
            self.assertTemplateUsed(
                res, 'infrastructure/parameters/service_config.html')

    def test_service_config_post(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        role = api.tuskar.Role(self.tuskarclient_roles.first())
        data = {
            'virt_type': 'qemu',
            'snmp_password': 'password',
        }
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.patch',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.get_role_by_name',
                  return_value=role),
        ):
            res = self.client.post(SERVICE_CONFIG_URL, data)
            self.assertRedirectsNoFollow(res, INDEX_URL)
