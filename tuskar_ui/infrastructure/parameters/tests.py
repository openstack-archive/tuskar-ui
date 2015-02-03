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
from mock import patch, call, ANY  # noqa
from openstack_dashboard.test.test_data import utils

from tuskar_ui import api
from tuskar_ui.test import helpers as test
from tuskar_ui.test.test_data import tuskar_data


INDEX_URL = urlresolvers.reverse(
    'horizon:infrastructure:parameters:index')
SIMPLE_SERVICE_CONFIG_URL = urlresolvers.reverse(
    'horizon:infrastructure:parameters:simple_service_configuration')
ADVANCED_SERVICE_CONFIG_URL = urlresolvers.reverse(
    'horizon:infrastructure:parameters:advanced_service_configuration')

TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)


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

    def test_simple_service_config_get(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        role = api.tuskar.Role(self.tuskarclient_roles.first())
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.get_role_by_name',
                  return_value=role),
        ):
            res = self.client.get(SIMPLE_SERVICE_CONFIG_URL)
            self.assertTemplateUsed(
                res, 'infrastructure/parameters/simple_service_config.html')

    def test_advanced_service_config_post(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        roles = [api.tuskar.Role(role)
                 for role in self.tuskarclient_roles.list()]
        parameters = [api.tuskar.Parameter(p, plan=self) for p in plan.parameters]

        data = {p.name: unicode(p.value) for p in parameters}

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.role_list',
                  return_value=roles),
            patch('tuskar_ui.api.tuskar.Plan.parameter_list',
                  return_value=parameters),
            patch('tuskar_ui.api.tuskar.Plan.patch',
                  return_value=plan),
        ) as (get_the_plan, role_list, parameter_list, plan_patch):
            res = self.client.post(ADVANCED_SERVICE_CONFIG_URL, data)

        self.assertRedirectsNoFollow(res, INDEX_URL)

        plan_patch.assert_called_once_with(ANY, plan.uuid, data)

    def test_simple_service_config_post(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        roles = [api.tuskar.Role(role) for role in
                 self.tuskarclient_roles.list()]
        plan.role_list = roles

        data = {
            'virt_type': 'qemu',
            'snmp_password': 'password',
            'cinder_iscsi_helper': 'lioadm',
            'cloud_name': 'cloud_name',
            'neutron_public_interface': 'eth0',
            'extra_config': '{}'
        }
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.get_the_plan',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.patch',
                  return_value=plan),
            patch('tuskar_ui.api.tuskar.Plan.get_role_by_name',
                  return_value=roles[0]),
        ) as (get_the_plan, plan_patch, get_role_by_name):
            res = self.client.post(SIMPLE_SERVICE_CONFIG_URL, data)

        self.assertRedirectsNoFollow(res, INDEX_URL)

        plan_patch.assert_called_once_with(ANY, plan.uuid, {
            'Controller-1::CloudName': u'cloud_name',
            'Controller-1::SnmpdReadonlyUserPassword': u'password',
            'Controller-1::NeutronPublicInterface': u'eth0',
            'Controller-1::CinderISCSIHelper': u'lioadm',
            'Controller-1::NovaComputeLibvirtType': u'qemu',
            'Compute-1::SnmpdReadonlyUserPassword': u'password',
            'Block Storage-1::SnmpdReadonlyUserPassword': u'password',
            'Object Storage-1::SnmpdReadonlyUserPassword': u'password',
            'Controller-1::NtpServer': u'',
            'Controller-1::ExtraConfig': u'{}',
            'Compute-1::ExtraConfig': u'{}',
            'Block Storage-1::ExtraConfig': u'{}',
            'Object Storage-1::ExtraConfig': u'{}'})
