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

import mock
from mock import patch  # noqa

from heatclient.v1 import events
from novaclient.v1_1 import servers

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class HeatAPITests(test.APITestCase):
    def test_overcloud_stack(self):
        stack = self.heatclient_stacks.first()
        ocs = api.heat.OvercloudStack(
            self.tuskarclient_overcloud_plans.first(),
            request=object())
        with patch('openstack_dashboard.api.heat.stack_get',
                   return_value=stack):
            ret_val = ocs
            self.assertIsInstance(ret_val, api.heat.OvercloudStack)

    def test_overcloud_stack_events(self):
        event_list = self.heatclient_events.list()
        stack = self.heatclient_stacks.first()

        with patch('openstack_dashboard.api.heat.events_list',
                   return_value=event_list):
            ret_val = api.heat.OvercloudStack(stack).events
        for e in ret_val:
            self.assertIsInstance(e, events.Event)
        self.assertEqual(8, len(ret_val))

    def test_overcloud_stack_is_deployed(self):
        stack = api.heat.OvercloudStack(self.heatclient_stacks.first())
        ret_val = stack.is_deployed
        self.assertFalse(ret_val)

    def test_overcloud_stack_resources(self):
        stack = api.heat.OvercloudStack(self.heatclient_stacks.first())

        resources = self.heatclient_resources.list()
        nodes = self.baremetalclient_nodes.list()
        instances = []

        with patch('openstack_dashboard.api.base.is_service_enabled',
                   return_value=False):
            with patch('openstack_dashboard.api.heat.resources_list',
                       return_value=resources):
                with patch('openstack_dashboard.api.nova.server_list',
                           return_value=(instances, None)):
                    with patch('novaclient.v1_1.contrib.baremetal.'
                               'BareMetalNodeManager.list',
                               return_value=nodes):
                        ret_val = stack.resources()

        for i in ret_val:
            self.assertIsInstance(i, api.heat.Resource)
        self.assertEqual(4, len(ret_val))

    def test_overcloud_stack_resources_no_ironic(self):
        stack = api.heat.OvercloudStack(self.heatclient_stacks.first())
        role = api.tuskar.OvercloudRole(
            self.tuskarclient_overcloud_roles.first())

        # FIXME(lsmola) only resources and image_name should be tested
        # here, anybody has idea how to do that?
        image = self.glanceclient_images.first()
        resources = self.heatclient_resources.list()
        instances = self.novaclient_servers.list()
        nodes = self.baremetalclient_nodes.list()
        with patch('openstack_dashboard.api.base.is_service_enabled',
                   return_value=False):
            with patch('openstack_dashboard.api.heat.resources_list',
                       return_value=resources) as resource_list:
                with patch('openstack_dashboard.api.nova.server_list',
                           return_value=(instances, None)) as server_list:
                    with patch('openstack_dashboard.api.glance.image_get',
                               return_value=image) as image_get:
                        with patch('novaclient.v1_1.contrib.baremetal.'
                                   'BareMetalNodeManager.list',
                                   return_value=nodes) as node_list:
                                ret_val = stack.resources_by_role(role)
                                self.assertEqual(resource_list.call_count, 1)
                                self.assertEqual(server_list.call_count, 1)
                                self.assertEqual(image_get.call_count, 2)
                                self.assertEqual(node_list.call_count, 1)

        for i in ret_val:
            self.assertIsInstance(i, api.heat.Resource)
        self.assertEqual(4, len(ret_val))

    def test_overcloud_stack_keystone_ip(self):
        stack = api.heat.OvercloudStack(self.heatclient_stacks.first())

        self.assertEqual('192.0.2.23', stack.keystone_ip)

    def test_overcloud_stack_dashboard_url(self):
        stack = api.heat.OvercloudStack(self.heatclient_stacks.first())
        stack._plan = api.tuskar.OvercloudPlan(
            self.tuskarclient_overcloud_plans.first())

        mocked_service = mock.Mock(id='horizon_id')
        mocked_service.name = 'horizon'

        services = [mocked_service]
        endpoints = [mock.Mock(service_id='horizon_id',
                               adminurl='http://192.0.2.23:/admin'), ]

        services_obj = mock.Mock(
            **{'list.return_value': services, })

        endpoints_obj = mock.Mock(
            **{'list.return_value': endpoints, })

        overcloud_keystone_client = mock.Mock(
            services=services_obj,
            endpoints=endpoints_obj)

        with patch('tuskar_ui.api.heat.overcloud_keystoneclient',
                   return_value=overcloud_keystone_client) as client_get:
            self.assertEqual(['http://192.0.2.23:/admin'],
                             stack.dashboard_urls)
            self.assertEqual(client_get.call_count, 1)

    def test_resource_get(self):
        stack = self.heatclient_stacks.first()
        resource = self.heatclient_resources.first()

        with patch('openstack_dashboard.api.heat.resource_get',
                   return_value=resource):
            with patch('openstack_dashboard.api.heat.stack_get',
                       return_value=stack):
                ret_val = api.heat.Resource.get(None, stack,
                                                resource.resource_name)
        self.assertIsInstance(ret_val, api.heat.Resource)

    def test_resource_node_no_ironic(self):
        resource = self.heatclient_resources.first()
        nodes = self.baremetalclient_nodes.list()
        instance = self.novaclient_servers.first()

        with patch('openstack_dashboard.api.base.is_service_enabled',
                   return_value=False):
            with patch('openstack_dashboard.api.nova.server_get',
                       return_value=instance):
                with patch('novaclient.v1_1.contrib.baremetal.'
                           'BareMetalNodeManager.list',
                           return_value=nodes):
                    ret_val = api.heat.Resource(
                        resource, request=object()).node
        self.assertIsInstance(ret_val, api.node.Node)
        self.assertIsInstance(ret_val.instance, servers.Server)
