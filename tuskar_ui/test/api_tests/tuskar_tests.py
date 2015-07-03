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

from __future__ import absolute_import
import contextlib

from mock import patch, call  # noqa

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class TuskarAPITests(test.APITestCase):
    def test_plan_create(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.create',
                   return_value=plan):
            ret_val = api.tuskar.Plan.create(self.request, {}, {})
        self.assertIsInstance(ret_val, api.tuskar.Plan)

    def test_plan_list(self):
        plans = self.tuskarclient_plans.list()

        with patch('tuskarclient.v2.plans.PlanManager.list',
                   return_value=plans):
            ret_val = api.tuskar.Plan.list(self.request)
        for plan in ret_val:
            self.assertIsInstance(plan, api.tuskar.Plan)
        self.assertEqual(1, len(ret_val))

    def test_plan_get(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.get',
                   return_value=plan):
            ret_val = api.tuskar.Plan.get(self.request, plan.uuid)

        self.assertIsInstance(ret_val, api.tuskar.Plan)

    def test_plan_get_the_plan(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.list',
                   return_value=[plan]):
            with patch('tuskarclient.v2.plans.PlanManager.create',
                       return_value=plan):
                ret_val = api.tuskar.Plan.get_the_plan(self.request)

        self.assertIsInstance(ret_val, api.tuskar.Plan)

    def test_plan_delete(self):
        plan = self.tuskarclient_plans.first()

        with patch('tuskarclient.v2.plans.PlanManager.delete',
                   return_value=None):
            api.tuskar.Plan.delete(self.request, plan.uuid)

    def test_plan_role_list(self):
        with patch('tuskarclient.v2.plans.PlanManager.get',
                   return_value=[]):
            plan = api.tuskar.Plan(self.tuskarclient_plans.first(),
                                   self.request)

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=self.tuskarclient_roles.list()):
            ret_val = plan.role_list
        self.assertEqual(4, len(ret_val))
        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.Role)

    def test_role_list(self):
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.Role.list(self.request)

        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.Role)
        self.assertEqual(4, len(ret_val))

    def test_role_get(self):
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.Role.get(self.request,
                                          roles[0].uuid)
        self.assertIsInstance(ret_val, api.tuskar.Role)

    def test_role_get_by_image(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        image = self.glanceclient_images.first()
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.Role.get_by_image(
                self.request, plan, image)
        self.assertIsInstance(ret_val, list)
        self.assertEqual(len(ret_val), 3)

    def test_parameter_stripped_name(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        param = plan.parameter('Controller-1::count')

        ret_val = param.stripped_name
        self.assertEqual(ret_val, 'count')

    def test_parameter_role(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first(),
                               request=self.request)
        param = plan.parameter('Controller-1::count')
        roles = self.tuskarclient_roles.list()

        with patch('tuskarclient.v2.roles.RoleManager.list',
                   return_value=roles):
            ret_val = param.role
        self.assertIsInstance(ret_val, api.tuskar.Role)
        self.assertEqual(ret_val.name, 'Controller')

    def test_list_generated_parameters(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.parameter_list',
                  return_value=plan.parameters),
        ) as (mock_parameter_list, ):
            ret_val = plan.list_generated_parameters()

        self.assertEqual(
            ret_val,
            {'Controller-1::KeystoneCACertificate': {
                'description': 'Keystone CA CertificateAdmin',
                'hidden': True,
                'name': 'Controller-1::KeystoneCACertificate',
                'value': 'unset',
                'default': '',
                'label': 'Keystone CA CertificateAdmin',
                'parameter_type': 'string',
                'constraints': []},
             'Controller-1::SnmpdReadonlyUserPassword': {
                'description': 'Snmpd password',
                'hidden': True,
                'name': 'Controller-1::SnmpdReadonlyUserPassword',
                'value': '',
                'default': '',
                'label': 'Snmpd password',
                'parameter_type': 'string',
                'constraints': []},
             'Controller-1::AdminPassword': {
                'description': 'Admin password',
                'hidden': True,
                'name': 'Controller-1::AdminPassword',
                'value': 'unset',
                'default': '',
                'label': 'Admin Password',
                'parameter_type': 'string',
                'constraints': []},
             'Controller-1::AdminToken': {
                'description': 'Admin Token',
                'hidden': True,
                'name': 'Controller-1::AdminToken',
                'value': '',
                'default': '',
                'label': 'Admin Token',
                'parameter_type': 'string',
                'constraints': []},
             'Compute-1::SnmpdReadonlyUserPassword': {
                'description': 'Snmpd password',
                'hidden': True,
                'name': 'Compute-1::SnmpdReadonlyUserPassword',
                'value': 'unset',
                'default': '',
                'label': 'Snmpd password',
                'parameter_type': 'string',
                'constraints': []}})

        mock_parameter_list.assert_called_once_with()

    def test_list_generated_parameters_without_prefix(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.parameter_list',
                  return_value=plan.parameters),
        ) as (mock_parameter_list, ):
            ret_val = plan.list_generated_parameters(with_prefix=False)

        self.assertEqual(
            ret_val,
            {'SnmpdReadonlyUserPassword': {
                'description': 'Snmpd password',
                'hidden': True,
                'name': 'Compute-1::SnmpdReadonlyUserPassword',
                'value': 'unset',
                'default': '',
                'label': 'Snmpd password',
                'parameter_type': 'string',
                'constraints': []},
             'KeystoneCACertificate': {
                'description': 'Keystone CA CertificateAdmin',
                'hidden': True,
                'name': 'Controller-1::KeystoneCACertificate',
                'value': 'unset',
                'default': '',
                'label': 'Keystone CA CertificateAdmin',
                'parameter_type': 'string',
                'constraints': []},
             'AdminToken': {
                'description': 'Admin Token',
                'hidden': True,
                'name': 'Controller-1::AdminToken',
                'value': '',
                'default': '',
                'label': 'Admin Token',
                'parameter_type': 'string',
                'constraints': []},
             'AdminPassword': {
                'description': 'Admin password',
                'hidden': True,
                'name': 'Controller-1::AdminPassword',
                'value': 'unset',
                'default': '',
                'label': 'Admin Password',
                'parameter_type': 'string',
                'constraints': []}})

        mock_parameter_list.assert_called_once_with()

    def test_make_keystone_certificates(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())
        with contextlib.nested(
            patch('os_cloud_config.keystone_pki.create_ca_pair',
                  return_value=('ca_key_pem', 'ca_cert_pem')),
            patch('os_cloud_config.keystone_pki.create_signing_pair',
                  return_value=('signing_key_pem', 'signing_cert_pem'))
        ) as (mock_create_ca_pair, mock_create_signing_pair):
            ret_val = plan._make_keystone_certificates(
                {'KeystoneSigningCertificate': {}})

        self.assertEqual(
            ret_val,
            {'KeystoneCACertificate': 'ca_cert_pem',
             'KeystoneSigningCertificate': 'signing_cert_pem',
             'KeystoneSigningKey': 'signing_key_pem'})

        mock_create_ca_pair.assert_called_once_with()
        mock_create_signing_pair.assert_called_once_with(
            'ca_key_pem', 'ca_cert_pem')

    def test_make_generated_parameters(self):
        plan = api.tuskar.Plan(self.tuskarclient_plans.first())

        with contextlib.nested(
            patch('tuskar_ui.api.tuskar.Plan.parameter_list',
                  return_value=plan.parameters),
            patch('tuskar_ui.api.tuskar.Plan._make_keystone_certificates',
                  return_value={'KeystoneCACertificate': 'ca_cert_pem'}),
            patch('tuskar_ui.api.tuskar.password_generator',
                  return_value='generated_password')
        ) as (mock_parameter_list, mock_make_keystone_certificates,
              mock_password_generator):
            ret_val = plan.make_generated_parameters()

        self.assertEqual(
            ret_val,
            {'Controller-1::KeystoneCACertificate': 'ca_cert_pem',
             'Controller-1::SnmpdReadonlyUserPassword': 'generated_password',
             'Controller-1::AdminPassword': 'generated_password',
             'Controller-1::AdminToken': 'generated_password',
             'Compute-1::SnmpdReadonlyUserPassword': 'generated_password'})

        mock_parameter_list.assert_has_calls([
            call(), call()])
        mock_make_keystone_certificates.assert_called_once_with({
            'SnmpdReadonlyUserPassword': {
                'description': 'Snmpd password',
                'hidden': True,
                'name': 'Compute-1::SnmpdReadonlyUserPassword',
                'value': 'unset',
                'default': '',
                'label': 'Snmpd password',
                'parameter_type': 'string',
                'constraints': []},
            'KeystoneCACertificate': {
                'description': 'Keystone CA CertificateAdmin',
                'hidden': True, 'name':
                'Controller-1::KeystoneCACertificate',
                'value': 'unset',
                'default': '',
                'label': 'Keystone CA CertificateAdmin',
                'parameter_type': 'string',
                'constraints': []},
            'AdminToken': {
                'description': 'Admin Token',
                'hidden': True,
                'name': 'Controller-1::AdminToken',
                'value': '',
                'default': '',
                'label': 'Admin Token',
                'parameter_type': 'string',
                'constraints': []},
            'AdminPassword': {
                'description': 'Admin password',
                'hidden': True,
                'name': 'Controller-1::AdminPassword',
                'value': 'unset',
                'default': '',
                'label': 'Admin Password',
                'parameter_type': 'string',
                'constraints': []}})
