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
import mock
from mock import patch  # noqa

from heatclient.v1 import events
from heatclient.v1 import stacks

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class TuskarAPITests(test.APITestCase):
    def test_overcloud_create(self):
        overcloud = self.tuskarclient_overclouds.first()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.create',
                   return_value=overcloud):
            ret_val = api.tuskar.Overcloud.create(self.request, {}, {})
        self.assertIsInstance(ret_val, api.tuskar.Overcloud)

    def test_overcloud_list(self):
        overclouds = self.tuskarclient_overclouds.list()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.list',
                   return_value=overclouds):
            ret_val = api.tuskar.Overcloud.list(self.request)
        for oc in ret_val:
            self.assertIsInstance(oc, api.tuskar.Overcloud)
        self.assertEqual(1, len(ret_val))

    def test_overcloud_get(self):
        overcloud = self.tuskarclient_overclouds.first()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.list',
                   return_value=[overcloud]):
            ret_val = api.tuskar.Overcloud.get(self.request, overcloud.id)

        self.assertIsInstance(ret_val, api.tuskar.Overcloud)

    def test_overcloud_delete(self):
        overcloud = self.tuskarclient_overclouds.first()
        with patch('tuskarclient.v1.overclouds.OvercloudManager.delete',
                   return_value=None):
            api.tuskar.Overcloud.delete(self.request, overcloud.id)

    def test_overcloud_stack(self):
        stack = self.heatclient_stacks.first()
        oc = api.tuskar.Overcloud(self.tuskarclient_overclouds.first(),
                                  request=object())
        with patch('openstack_dashboard.api.heat.stack_get',
                   return_value=stack):
            ret_val = oc.stack
            self.assertIsInstance(ret_val, stacks.Stack)

    def test_overcloud_stack_events(self):
        overcloud = self.tuskarclient_overclouds.first()
        event_list = self.heatclient_events.list()
        stack = self.heatclient_stacks.first()

        with patch('openstack_dashboard.api.heat.stack_get',
                   return_value=stack):
            with patch('openstack_dashboard.api.heat.events_list',
                       return_value=event_list):
                ret_val = api.tuskar.Overcloud(overcloud).stack_events
        for e in ret_val:
            self.assertIsInstance(e, events.Event)
        self.assertEqual(8, len(ret_val))

    def test_overcloud_stack_events_empty(self):
        overcloud = self.tuskarclient_overclouds.first()
        event_list = self.heatclient_events.list()
        overcloud.stack_id = None

        with patch('openstack_dashboard.api.heat.stack_get',
                   return_value=None):
            with patch('openstack_dashboard.api.heat.events_list',
                       return_value=event_list):
                ret_val = api.tuskar.Overcloud(overcloud).stack_events

        self.assertListEqual([], ret_val)

    def test_overcloud_is_deployed(self):
        stack = self.heatclient_stacks.first()
        oc = api.tuskar.Overcloud(self.tuskarclient_overclouds.first(),
                                  request=object())
        with patch('openstack_dashboard.api.heat.stack_get',
                   return_value=stack):
            ret_val = oc.is_deployed
            self.assertFalse(ret_val)

    def test_overcloud_all_resources(self):
        oc = api.tuskar.Overcloud(self.tuskarclient_overclouds.first(),
                                  request=object())

        # FIXME(lsmola) the stack call should not be tested in this unit test
        # anybody has idea how to do it?
        stack = self.heatclient_stacks.first()
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
                        with patch('openstack_dashboard.api.heat.stack_get',
                                   return_value=stack):
                            ret_val = oc.all_resources()

        for i in ret_val:
            self.assertIsInstance(i, api.heat.Resource)
        self.assertEqual(4, len(ret_val))

    def test_overcloud_resources_no_ironic(self):
        oc = api.tuskar.Overcloud(self.tuskarclient_overclouds.first(),
                                  request=object())
        role = api.tuskar.OvercloudRole(
            self.tuskarclient_overcloud_roles.first())

        # FIXME(lsmola) only all_resources and image_name should be tested
        # here, anybody has idea how to do that?
        image = self.glanceclient_images.first()
        stack = self.heatclient_stacks.first()
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
                            with patch(
                                    'openstack_dashboard.api.heat.stack_get',
                                    return_value=stack) as stack_get:
                                ret_val = oc.resources(role)
                                self.assertEqual(resource_list.call_count, 1)
                                self.assertEqual(server_list.call_count, 1)
                                self.assertEqual(image_get.call_count, 2)
                                self.assertEqual(node_list.call_count, 1)
                                self.assertEqual(stack_get.call_count, 1)

        for i in ret_val:
            self.assertIsInstance(i, api.heat.Resource)
        self.assertEqual(4, len(ret_val))

    def test_overcloud_keystone_ip(self):
        oc = api.tuskar.Overcloud(self.tuskarclient_overclouds.first(),
                                  request=object())
        stack = self.heatclient_stacks.first()

        with contextlib.nested(
            patch('openstack_dashboard.api.heat.stack_get',
                  return_value=stack)) as (stack_get, ):
                self.assertEqual('192.0.2.23', oc.keystone_ip)
                self.assertEqual(stack_get.call_count, 1)

    def test_overcloud_dashboard_url(self):
        oc = api.tuskar.Overcloud(self.tuskarclient_overclouds.first(),
                                  request=object())
        stack = self.heatclient_stacks.first()

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

        with contextlib.nested(
            patch('openstack_dashboard.api.heat.stack_get',
                  return_value=stack),
            patch('tuskar_ui.api.tuskar.overcloud_keystoneclient',
                  return_value=overcloud_keystone_client)
        ) as (stack_get, client_get):
            self.assertEqual(['http://192.0.2.23:/admin'],
                             oc.dashboard_urls)
            self.assertEqual(stack_get.call_count, 1)
            self.assertEqual(client_get.call_count, 1)

    def test_overcloud_role_list(self):
        roles = self.tuskarclient_overcloud_roles.list()

        with patch('tuskarclient.v1.overcloud_roles.OvercloudRoleManager.list',
                   return_value=roles):
            ret_val = api.tuskar.OvercloudRole.list(self.request)

        for r in ret_val:
            self.assertIsInstance(r, api.tuskar.OvercloudRole)
        self.assertEqual(4, len(ret_val))

    def test_overcloud_role_get(self):
        role = self.tuskarclient_overcloud_roles.first()

        with patch('tuskarclient.v1.overcloud_roles.OvercloudRoleManager.get',
                   return_value=role):
            ret_val = api.tuskar.OvercloudRole.get(self.request, role.id)

        self.assertIsInstance(ret_val, api.tuskar.OvercloudRole)

    def test_overcloud_role_get_by_node(self):
        node = api.node.Node(
            api.node.BareMetalNode(self.baremetalclient_nodes.first()))
        instance = self.novaclient_servers.first()
        image = self.glanceclient_images.first()
        roles = self.tuskarclient_overcloud_roles.list()

        with contextlib.nested(
                patch('tuskarclient.v1.overcloud_roles.'
                      'OvercloudRoleManager.list',
                      return_value=roles),
                patch('openstack_dashboard.api.nova.server_get',
                      return_value=instance),
                patch('openstack_dashboard.api.glance.image_get',
                      return_value=image),
        ):
            ret_val = api.tuskar.OvercloudRole.get_by_node(self.request,
                                                           node)
        self.assertEqual(ret_val.name, 'Controller')
