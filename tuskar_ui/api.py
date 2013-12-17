# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from openstack_dashboard.api import base

from tuskar_ui.cached_property import cached_property  # noqa

class Stack(base.APIResourceWrapper):
    _attrs = ['id', 'stack_name', 'stack_status', ]

    @classmethod
    def create(cls, request, **kwargs):
        # deploy a Stack through Heat
        # we're passing in sizing information
        # ? heatclient.stacks.create('overcloud', ..)
        # ? I assume more processing needed to create template?

    @classmethod
    def get(cls, request):
        # retrieve a Stack.  For the first release,
        # we will only get one
        # ? heatclient.stacks.get('overcloud')

    @cached_property
    def resources(self):
        # retrieve Resources for this Stack
        # ? heatclient.resources.list(self.id)

    @cached_property
    def nodes(self):
        # retrieve Nodes associated with this Stack
        # ? match node.instance_uuid and resource.physical_resource_id


class Node(base.APIResourceWrapper):
    # ? not entirely sure what's available from Ironic here
    _attrs = ['uuid']

    @classmethod
    def create(cls, request, **kwargs):
        # create a node through ironic
        # ? ironicclient.nodes.create(..)

    @classmethod
    def get(cls, request, uuid):
        # retrieve a node through ironic
        # ? ironicclient.nodes.get(uuid)

    @classmethod
    def list(cls, request):
        # list nodes through ironic
        # ? ironicclient.nodes.list()

    @classmethod
    def delete(cls, request, id):
        # remove a node from ironic

    @classmethod
    def free(cls, request):
        # list nodes through ironic
        # ? Nodes.list - Stack.nodes

    @cached_property
    def resource(self):
        # retrieve resource running on the node
        # ? match node.instance_uuid and resource.physical_resource_id


class Resource(base.APIResourceWrapper):
    _attrs = ['resource_name', 'resource_type', 'resource_status']

    @classmethod
    def get(cls, request, stack, resource_name):
        # retrieve resource through heat
        # ? heatclient.resources.get(stack.id, resource_name)

    @cached_property
    def node(self):
        # node that resource is running on
        # ? match resource.physical_resource_id and node.instance_uuid

    @cached_property
    def resource_category(self):
        # category that resource belongs to
        # ? ResourceCategory({name: self.resource_type})


# ? hardcoded somewhere?
class ResourceCategory(base.APIResourceWrapper):
    _attrs = ['name', 'resource_type']

    @cached_property
    def image(self):
        # ? return pre-existing image

    @cached_property
    def resources(self, stack):
        # retrieve all resources of this category
        # ? filter Stack.resources by resource_type
