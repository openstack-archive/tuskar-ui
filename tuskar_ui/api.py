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

import logging

import django.conf

from horizon.utils import memoized

from openstack_dashboard.api import base
from openstack_dashboard.test.test_data import utils
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.test.test_data import tuskar_data
from tuskarclient.v1 import client as tuskar_client

LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(django.conf.settings, 'TUSKAR_ENDPOINT_URL')


# TODO(Tzu-Mainn Chen): remove test data when possible
def test_data():
    test_data = utils.TestDataContainer()
    tuskar_data.data(test_data)
    return test_data


# FIXME: request isn't used right in the tuskar client right now, but looking
# at other clients, it seems like it will be in the future
def tuskarclient(request):
    c = tuskar_client.Client(TUSKAR_ENDPOINT_URL)
    return c


def list_to_dict(object_list, key_attribute='id'):
    """Converts an object list to a dict

    :param object_list: list of objects to be put into a dict
    :type  object_list: list

    :param key_attribute: object attribute used as index by dict
    :type  key_attribute: str

    :return: dict containing the objects in the list
    :rtype: dict
    """
    return dict((getattr(o, key_attribute), o) for o in object_list)


# TODO(Tzu-Mainn Chen): change this to APIResourceWrapper once
# ResourceCategory object exists in tuskar
class Overcloud(base.APIDictWrapper):
    _attrs = ('id', 'stack_id', 'name', 'description')

    @classmethod
    def create(cls, request, overcloud_sizing):
        """Create an Overcloud in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_sizing: overcloud sizing information
        :type  overcloud_sizing: dict (structure to be determined
                                 by tuskar api)

        :return: the created Overcloud object
        :rtype:  tuskar_ui.api.Overcloud
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # overcloud = tuskarclient(request).overclouds.create(
        #                          'overcloud',
        #                          overcloud_sizing)
        overcloud = test_data().tuskarclient_overclouds.first()

        return cls(overcloud)

    @classmethod
    def list(cls, request):
        """Return a list of Overclouds in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Overclouds, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Overcloud
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # ocs = tuskarclient(request).overclouds.list()
        ocs = test_data().tuskarclient_overclouds.list()

        return [cls(oc) for oc in ocs]

    @classmethod
    def get(cls, request, overcloud_id):
        """Return the Tuskar Overcloud that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_id: ID of Overcloud to be retrieved
        :type  overcloud_id: int

        :return: matching Overcloud, or None if no Overcloud matches
                 the ID
        :rtype:  tuskar_ui.api.Overcloud
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # overcloud = tuskarclient(request).overclouds.get(overcloud_id)
        overcloud = test_data().tuskarclient_overclouds.first()

        return cls(overcloud)

    @cached_property
    def stack(self):
        """Return the Heat Stack associated with this Overcloud

        :return: Heat Stack associated with this Overcloud; or None
                 if no Stack is associated, or no Stack can be
                 found
        :rtype:  heatclient.v1.stacks.Stack
        """
        if self.stack_id:
            # TODO(Tzu-Mainn Chen): remove test data when possible
            # stack = heatclient(request).stacks.get(self.stack_id)
            stack = test_data().heatclient_stacks.first()
            return stack
        return None

    @cached_property
    def stack_events(self):
        """Return the Heat Events associated with this Overcloud

        :return: list of Heat Events associated with this Overcloud;
                 or an empty list if there is no Stack associated with
                 this Overcloud, or there are no Events
        :rtype:  list of heatclient.v1.events.Event
        """
        if self.stack_id:
            # TODO(Tzu-Mainn Chen): remove test data when possible
            # events = heatclient(request).events.get(self.stack_id)
            events = test_data().heatclient_events.list()
            return events
        return []

    @cached_property
    def is_deployed(self):
        """Check if this Overcloud is successfully deployed.

        :return: True if this Overcloud is successfully deployed;
                 False otherwise
        :rtype:  bool
        """
        # TODO(rdopieralski) Actually implement it
        return False

    @memoized.memoized
    def resources(self, resource_category, with_joins=False):
        """Return a list of Overcloud Resources that match a Resource Category

        :param resource_category: category of resources to be returned
        :type  resource_category: tuskar_ui.api.ResourceCategory

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Resource?
        :type  with_joins: bool

        :return: list of Overcloud Resources that match the Resource Category,
                 or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Resource
        """
        # TODO(Tzu-Mainn Chen): uncomment when possible
        #resources = tuskarclient(request).overclouds.get_resources(
        #    self.id, resource_category.id)
        resources = [r for r in test_data().heatclient_resources.list()
                     if r.logical_resource_id.startswith(
                         resource_category.name)]

        if not with_joins:
            return [Resource(r) for r in resources]

        nodes_dict = list_to_dict(Node.list(None, associated=True),
                                  key_attribute='instance_uuid')
        joined_resources = []
        for r in resources:
            node = nodes_dict.get(r.physical_resource_id, None)
            joined_resources.append(Resource(r,
                                             node=node))
        return joined_resources

    @memoized.memoized
    def nodes(self, resource_category):
        """Return a list of Nodes in the Overcloud that match a
        Resource Category

        :param resource_category: category of resources to retrieve
                                  instances from
        :type  resource_category: tuskar_ui.api.ResourceCategory

        :return: list of Nodes in the Overcloud that match a Resource
                 Category, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Node
        """
        resources = self.resources(resource_category, with_joins=True)
        return [r.node for r in resources]


class Node(base.APIResourceWrapper):
    _attrs = ('uuid', 'instance_uuid', 'driver', 'driver_info',
              'properties', 'power_state')

    def __init__(self, apiresource, instance=None):
        super(Node, self).__init__(apiresource)
        if instance is not None:
            self._instance = instance

    @classmethod
    def create(cls, request, ipmi_address, cpu, ram, local_disk,
               mac_addresses, ipmi_username=None, ipmi_password=None):
        """Create a Node in Ironic

        :param request: request object
        :type  request: django.http.HttpRequest

        :param ipmi_address: IPMI address
        :type  ipmi_address: str

        :param cpu: number of cores
        :type  cpu: int

        :param ram: RAM in GB
        :type  ram: int

        :param local_disk: local disk in TB
        :type  local_disk: int

        :param mac_addresses: list of mac addresses
        :type  mac_addresses: list of str

        :param ipmi_username: IPMI username
        :type  ipmi_username: str

        :param ipmi_password: IPMI password
        :type  ipmi_password: str

        :return: the created Node object
        :rtype:  tuskar_ui.api.Node
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # TODO(Tzu-Mainn Chen): transactionality?
        # node = ironicclient(request).node.create(
        #     driver='pxe_ipmitool',
        #     driver_info={'ipmi_address': ipmi_address,
        #                  'ipmi_username': ipmi_username,
        #                  'password': ipmi_password},
        #     properties={'cpu': cpu,
        #                  'ram': ram,
        #                  'local_disk': local_disk})
        # for mac_address in mac_addresses:
        #     ironicclient(request).port.create(
        #         node_uuid=node.uuid,
        #         address=mac_address
        #     )
        node = test_data().ironicclient_nodes.first()

        return cls(node)

    @classmethod
    def get(cls, request, uuid):
        """Return the Node in Ironic that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of Node to be retrieved
        :type  uuid: str

        :return: matching Node, or None if no Node matches the ID
        :rtype:  tuskar_ui.api.Node
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # node = ironicclient(request).nodes.get(uuid)
        nodes = test_data().ironicclient_nodes.list()
        node = next((n for n in nodes if uuid == n.uuid),
                    None)
        if node.instance_uuid is not None:
            # server = novaclient(request).servers.get(node.instance_uuid)
            servers = test_data().novaclient_servers.list()
            server = next((s for s in servers if node.instance_uuid == s.id),
                          None)
            return cls(node, instance=server)

        return cls(node)

    @classmethod
    def get_by_instance_uuid(cls, request, instance_uuid):
        """Return the Node in Ironic associated with the instance ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param instance_uuid: ID of Instance that is deployed on the Node
                              to be retrieved
        :type  instance_uuid: str

        :return: matching Node
        :rtype:  tuskar_ui.api.Node

        :raises: ironicclient.exc.HTTPNotFound if there is no Node with the
                 matching instance UUID
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        #node = ironicclient(request).nodes.get_by_instance_uuid(
        #    instance_uuid)
        #server = novaclient(request).servers.get(instance_id)
        nodes = test_data().ironicclient_nodes.list()
        node = next((n for n in nodes if instance_uuid == n.instance_uuid),
                    None)
        servers = test_data().novaclient_servers.list()
        server = next((s for s in servers if instance_uuid == s.id),
                      None)

        return cls(node, instance=server)

    @classmethod
    def list(cls, request, associated=None):
        """Return a list of Nodes in Ironic

        :param request: request object
        :type  request: django.http.HttpRequest

        :param associated: should we also retrieve all Nodes, only those
                           associated with an Instance, or only those not
                           associated with an Instance?
        :type  associated: bool

        :return: list of Nodes, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Node
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # nodes = ironicclient(request).nodes.list(
        #    associated=associated)
        nodes = test_data().ironicclient_nodes.list()

        if associated is not None:
            if associated:
                nodes = [node for node in nodes
                         if node.instance_uuid is not None]
            else:
                nodes = [node for node in nodes
                         if node.instance_uuid is None]
                return [cls(node) for node in nodes]

        # servers = novaclient(request).servers.list(detailed=True)
        servers_dict = list_to_dict(test_data().novaclient_servers.list())
        nodes_with_instance = []
        for n in nodes:
            server = servers_dict.get(n.instance_uuid, None)
            nodes_with_instance.append(cls(n, instance=server))

        return nodes_with_instance

    @classmethod
    def delete(cls, request, uuid):
        """Remove the Node matching the ID from Ironic if it
        exists; otherwise, does nothing.

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of Node to be removed
        :type  uuid: str
        """
        # TODO(Tzu-Mainn Chen): uncomment when possible
        # ironicclient(request).nodes.delete(uuid)
        return

    @cached_property
    def instance(self):
        """Return the Nova Instance associated with this Resource

        :return: Nova Instance associated with this Resource; or
                 None if there is no Instance associated with this
                 Resource, or no matching Instance is found
        :rtype:  tuskar_ui.api.Instance
        """
        if hasattr(self, '_instance'):
            return self._instance
        if self.instance_uuid:
            # TODO(Tzu-Mainn Chen): remove test data when possible
            # server = novaclient(request).servers.get(self.instance_uuid)
            servers = test_data().novaclient_servers.list()
            server = next((s for s in servers if self.instance_uuid == s.id),
                          None)

            return server
        return None

    @cached_property
    def addresses(self):
        """Return a list of port addresses associated with this Node

        :return: list of port addresses associated with this Node, or
                 an empty list if no addresses are associated with
                 this Node
        :rtype:  list of str
        """
        # TODO(Tzu-Mainn Chen): uncomment when possible
        # ports = self.list_ports()
        ports = test_data().ironicclient_ports.list()[:2]

        return [port.address for port in ports]


class Resource(base.APIResourceWrapper):
    _attrs = ('resource_name', 'resource_type', 'resource_status',
              'physical_resource_id')

    def __init__(self, apiresource, **kwargs):
        super(Resource, self).__init__(apiresource)
        if 'node' in kwargs:
            self._node = kwargs['node']

    @classmethod
    def get(cls, request, overcloud, resource_name):
        """Return the specified Heat Resource within an Overcloud

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud: the Overcloud from which to retrieve the resource
        :type  overcloud: tuskar_ui.api.Overcloud

        :param resource_name: name of the Resource to retrieve
        :type  resource_name: str

        :return: matching Resource, or None if no Resource in the Overcloud
                 stack matches the resource name
        :rtype:  tuskar_ui.api.Resource
        """
        # TODO(Tzu-Mainn Chen): uncomment when possible
        # resource = heatclient(request).resources.get(
        #     overcloud.id,
        #     resource_name)
        resources = test_data().heatclient_resources.list()
        resource = next((r for r in resources
                         if overcloud['id'] == r.stack_id
                         and resource_name == r.resource_name),
                        None)

        return cls(resource)

    @cached_property
    def node(self):
        """Return the Ironic Node associated with this Resource

        :return: Ironic Node associated with this Resource, or None if no
                 Node is associated
        :rtype:  tuskar_ui.api.Node

        :raises: ironicclient.exc.HTTPNotFound if there is no Node with the
                 matching instance UUID
        """
        if hasattr(self, '_node'):
            return self._node
        if self.physical_resource_id:
            return Node.get_by_instance_uuid(None, self.physical_resource_id)
        return None


# TODO(Tzu-Mainn Chen): change this to APIResourceWrapper once
# ResourceCategory object exists in tuskar
class ResourceCategory(base.APIDictWrapper):
    _attrs = ('id', 'name', 'description', 'image_id')

    @classmethod
    def list(cls, request):
        """Return a list of Resource Categories in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Resource Categories, or an empty list if there
                 are none
        :rtype:  list of tuskar_ui.api.ResourceCategory
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # categories = tuskarclient(request).resource_categories.list()
        rcs = test_data().tuskarclient_resource_categories.list()
        return [cls(rc) for rc in rcs]

    @classmethod
    def get(cls, request, category_id):
        """Return the Tuskar ResourceCategory that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param category_id: ID of ResourceCategory to be retrieved
        :type  category_id: int

        :return: matching ResourceCategory, or None if no matching
                 ResourceCategory can be found
        :rtype:  tuskar_ui.api.ResourceCategory
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # category = tuskarclient(request).resource_categories.get(category_id)
        categories = ResourceCategory.list(request)
        category = next((c for c in categories if category_id == str(c.id)),
                        None)

        return cls(category)

    @cached_property
    def image(self):
        """Return the Glance Image associated with this ResourceCategory

        :return: Glance Image associated with this ResourceCategory; or
                 None if no Image is associated, or if no matching Image
                 can be found
        :rtype:  glanceclient.v1.images.Image
        """
        if self.image_id:
            # TODO(Tzu-Mainn Chen): remove test data when possible
            # image = glanceclient(request).images.get(self.image_id)
            images = test_data().glanceclient_images.list()
            image = next((i for i in images if self.image_id == i.id),
                         None)
            return image
        return None
