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

from mock import patch  # noqa

from novaclient.v1_1 import servers

from tuskar_ui import api
from tuskar_ui.test import helpers as test


class HeatAPITests(test.APITestCase):

    def test_resource_get(self):
        stack = self.heatclient_stacks.first()
        overcloud = api.tuskar.Overcloud(self.tuskarclient_overclouds.first(),
                                         request=object())
        resource = self.heatclient_resources.first()

        with patch('openstack_dashboard.api.heat.resource_get',
                   return_value=resource):
            with patch('openstack_dashboard.api.heat.stack_get',
                       return_value=stack):
                ret_val = api.heat.Resource.get(None, overcloud,
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
