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

from openstack_dashboard.test.test_data import utils as test_data_utils

from glanceclient.v1 import images
from heatclient.v1 import events
from heatclient.v1 import resources
from heatclient.v1 import stacks
from novaclient.v1_1 import servers


def data(TEST):

    # Stack
    TEST.heatclient_stacks = test_data_utils.TestDataContainer()
    stack_1 = stacks.Stack(
        stacks.StackManager(None),
        {'id': 'stack-id-1',
         'stack_name': 'overcloud',
         'stack_status': 'RUNNING',
         'outputs': [{
             'output_key': 'KeystoneURL',
             'output_value': 'http://192.0.2.23:5000/v2',
         }],
         'parameters': {
             'plan_id': 'plan-1',
             'one': 'one',
             'two': 'two',
         }})
    TEST.heatclient_stacks.add(stack_1)

    # Events
    TEST.heatclient_events = test_data_utils.TestDataContainer()
    event_1 = events.Event(
        events.EventManager(None),
        {'id': 1,
         'stack_id': 'stack-id-1',
         'resource_name': 'Controller',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:26:15Z'})
    event_2 = events.Event(
        events.EventManager(None),
        {'id': 2,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute0',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:26:27Z'})
    event_3 = events.Event(
        events.EventManager(None),
        {'id': 3,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute1',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:26:44Z'})
    event_4 = events.Event(
        events.EventManager(None),
        {'id': 4,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute0',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:27:14Z'})
    event_5 = events.Event(
        events.EventManager(None),
        {'id': 5,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute2',
         'resource_status': 'CREATE_IN_PROGRESS',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:27:31Z'})
    event_6 = events.Event(
        events.EventManager(None),
        {'id': 6,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute1',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:28:01Z'})
    event_7 = events.Event(
        events.EventManager(None),
        {'id': 7,
         'stack_id': 'stack-id-1',
         'resource_name': 'Controller',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:28:59Z'})
    event_8 = events.Event(
        events.EventManager(None),
        {'id': 8,
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute2',
         'resource_status': 'CREATE_COMPLETE',
         'resource_status_reason': 'state changed',
         'event_time': '2014-01-01T07:29:11Z'})
    TEST.heatclient_events.add(event_1, event_2, event_3, event_4,
                               event_5, event_6, event_7, event_8)

    # Resource
    TEST.heatclient_resources = test_data_utils.TestDataContainer()
    resource_1 = resources.Resource(
        resources.ResourceManager(None),
        {'id': '1-resource-id',
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute0',
         'logical_resource_id': 'Compute0',
         'physical_resource_id': 'aa',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'Compute'})
    resource_2 = resources.Resource(
        resources.ResourceManager(None),
        {'id': '2-resource-id',
         'stack_id': 'stack-id-1',
         'resource_name': 'Controller',
         'logical_resource_id': 'Controller',
         'physical_resource_id': 'bb',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'Controller'})
    resource_3 = resources.Resource(
        resources.ResourceManager(None),
        {'id': '3-resource-id',
         'stack_id': 'stack-id-1',
         'resource_name': 'Compute1',
         'logical_resource_id': 'Compute1',
         'physical_resource_id': 'cc',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'Compute'})
    resource_4 = resources.Resource(
        resources.ResourceManager(None),
        {'id': '4-resource-id',
         'stack_id': 'stack-id-4',
         'resource_name': 'Compute2',
         'logical_resource_id': 'Compute2',
         'physical_resource_id': 'dd',
         'resource_status': 'CREATE_COMPLETE',
         'resource_type': 'Compute'})
    TEST.heatclient_resources.add(resource_1,
                                  resource_2,
                                  resource_3,
                                  resource_4)

    # Server
    TEST.novaclient_servers = test_data_utils.TestDataContainer()
    s_1 = servers.Server(
        servers.ServerManager(None),
        {'id': 'aa',
         'name': 'Compute',
         'image': {'id': 1},
         'flavor': {
             'id': '1',
         },
         'status': 'ACTIVE'})
    s_2 = servers.Server(
        servers.ServerManager(None),
        {'id': 'bb',
         'name': 'Controller',
         'image': {'id': 2},
         'flavor': {
             'id': '2',
         },
         'status': 'ACTIVE'})
    s_3 = servers.Server(
        servers.ServerManager(None),
        {'id': 'cc',
         'name': 'Compute',
         'image': {'id': 1},
         'flavor': {
             'id': '1',
         },
         'status': 'BUILD'})
    s_4 = servers.Server(
        servers.ServerManager(None),
        {'id': 'dd',
         'name': 'Compute',
         'image': {'id': 1},
         'flavor': {
             'id': '1',
         },
         'status': 'ERROR'})
    TEST.novaclient_servers.add(s_1, s_2, s_3, s_4)

    # Image
    TEST.glanceclient_images = test_data_utils.TestDataContainer()
    image_1 = images.Image(
        images.ImageManager(None),
        {'id': '2',
         'name': 'overcloud-control'})
    image_2 = images.Image(
        images.ImageManager(None),
        {'id': '1',
         'name': 'overcloud-compute'})
    image_3 = images.Image(
        images.ImageManager(None),
        {'id': '3',
         'name': 'Object Storage Image'})
    image_4 = images.Image(
        images.ImageManager(None),
        {'id': '4',
         'name': 'Block Storage Image'})
    TEST.glanceclient_images.add(image_1, image_2, image_3, image_4)
