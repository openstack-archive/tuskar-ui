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

from novaclient.v1_1.contrib import baremetal
from openstack_dashboard.test.test_data import utils
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.test.test_data import tuskar_data
from tuskarclient.v1 import client as tuskar_client

from openstack_dashboard.api import glance
from openstack_dashboard.api import heat
from openstack_dashboard.api import nova

LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(django.conf.settings, 'TUSKAR_ENDPOINT_URL')


def baremetalclient(request):
    nc = nova.novaclient(request)
    return baremetal.BareMetalNodeManager(nc)


# TODO(Tzu-Mainn Chen): remove test data when possible
def test_data():
    test_data = utils.TestDataContainer()
    tuskar_data.data(test_data)
    return test_data


# FIXME: request isn't used right in the tuskar client right now,
# but looking at other clients, it seems like it will be in the future
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


# FIXME(lsmola) This should be done in Horizon
# but i want to test that the real api is not called every time
# and I don't know how to mock client call
@memoized.memoized
def image_get(request, image_id):
    """Returns an Image object populated with metadata for image
    with supplied identifier.
    """
    image = glance.image_get(request, image_id)
    return image


# TODO(Tzu-Mainn Chen): change this to APIResourceWrapper once
# ResourceCategory object exists in tuskar
class Overcloud(base.APIDictWrapper):
    _attrs = ('id', 'stack_id', 'name', 'description')

    def __init__(self, apiresource, **kwargs):
        super(Overcloud, self).__init__(apiresource)
        if 'request' in kwargs:
            self._request = kwargs['request']

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

        return cls(overcloud, request=request)

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

        return [cls(oc, request=request) for oc in ocs]

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

        return cls(overcloud, request=request)

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
            # stack = test_data().heatclient_stacks.first()
            stack = heat.stack_get(self._request, 'overcloud')
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
        return self.stack.stack_status in ('CREATE_COMPLETE',
                                           'UPDATE_COMPLETE')

    @memoized.memoized
    def all_resources(self, with_joins=False):
        resources = [r for r in heat.resources_list(self._request,
                                                    self.stack.stack_name)]

        if not with_joins:
            return [Resource(r) for r in resources]

        instances_dict = list_to_dict(Instance.list(self._request,
                                                    with_joins=True))
        nodes_dict = list_to_dict(Node.list(self._request, associated=True),
                                  key_attribute='instance_uuid')

        joined_resources = []
        for r in resources:
            instance = instances_dict.get(r.physical_resource_id, None)
            node = nodes_dict.get(r.physical_resource_id, None)
            joined_resources.append(Resource(r,
                                             instance=instance,
                                             node=node))

        # I want just resources with nova instance
        return [r for r in joined_resources if r.instance is not None]

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
        # FIXME(lsmola) with_joins is not necessary here, I need at least
        # nova instance
        all_resources = self.all_resources(with_joins=True)
        filtered_resources = [resource for resource in all_resources if
                              (resource.instance.image_name ==
                               resource_category.image_name)]

        return filtered_resources

    @memoized.memoized
    def instances(self, resource_category):
    # FIXME(lsmola) we don't need this, we don't even need Instance class
    # deleting in follow up patch. We will not access instance without
    # resource context anywhere. (we shouldn't it complicate things-> number
    # of requests), for this reason, there are 2 Node.list queries instead on
    # 1. All we need is Resource and Node as separate entities.

        """Return a list of Instances in the Overcloud that match a
        Resource Category

        :param resource_category: category of resources to retrieve
                                  instances from
        :type  resource_category: tuskar_ui.api.ResourceCategory

        :return: list of Instances in the Overcloud that match a Resource
                 Category, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Instance
        """
        resources = self.resources(resource_category, with_joins=True)
        return [r.instance for r in resources]


# FIXME(lsmola) get rid of this class, or make it just dumb wrapper
class Instance(object):
    _attrs = ('id', 'name', 'image', 'status')

    def __init__(self, apiresource, **kwargs):
        if 'node' in kwargs:
            self._node = kwargs['node']
        if 'request' in kwargs:
            self._request = kwargs['request']

        # setting _attrs on this object
        for attr in Instance._attrs:
            setattr(self, attr, getattr(apiresource, attr, None))

    @classmethod
    def get(cls, request, instance_id):
        """Return the Nova Instance that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param instance_id: ID of Instance to be retrieved
        :type  instance_id: str

        :return: matching Instance, or None if no Instance matches
                 the ID
        :rtype:  tuskar_ui.api.Instance
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # instance = novaclient(request).servers.get(instance_id)
        server = nova.server_get(request, instance_id)

        return cls(server, request=request)

    @classmethod
    def list(cls, request, with_joins=False):
        """Return a list of Instances in Nova

        :param request: request object
        :type  request: django.http.HttpRequest

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Instance?
        :type  with_joins: bool

        :return: list of Instances, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Instance
        """
        # TODO(Tzu-Mainn Chen): remove test data when possible
        # servers = novaclient(request).servers.list(detailed=True)
        servers, has_more_data = nova.server_list(request)

        if not with_joins:
            return [cls(s) for s in servers]

        # FIXME(lsmola) this is doing extra api request, that is why i will
        # delete this whole class. Alternatively, optimize this.
        nodes_dict = list_to_dict(Node.list(request, associated=True),
                                  key_attribute='instance_uuid')
        joined_servers = []
        for s in servers:
            node = nodes_dict.get(s.id, None)
            joined_servers.append(Instance(s, node=node, request=request))
        return joined_servers

    @cached_property
    def node(self):
        """Return the Ironic Node associated with this Instance

        :return: Ironic Node associated with this Instance
        :rtype:  tuskar_ui.api.Node

        :raises: ironicclient.exc.HTTPNotFound if there is no Node with the
                 matching instance UUID
        """
        if hasattr(self, '_node'):
            return self._node
        return Node.get_by_instance_uuid(self._request, self.id)

    @cached_property
    def image_name(self):
        return image_get(self._request, self.image['id']).name


class Node(base.APIResourceWrapper):
    # FIXME(lsmola) uncomment this and delete equivalent methods
    #_attrs = ('uuid', 'instance_uuid', 'driver', 'driver_info',
    #          'properties', 'power_state')
    _attrs = ('id', 'uuid', 'instance_uuid')

    @classmethod
    def nova_baremetal_format(cls, ipmi_address, cpu, ram, local_disk,
                              mac_addresses, ipmi_username=None,
                              ipmi_password=None):
        """Converts Ironic parameters to Nova-baremetal format
        """
        return {'service_host': 'undercloud',
                'cpus': cpu,
                'memory_mb': ram,
                'local_gb': local_disk,
                'prov_mac_address': mac_addresses,
                'pm_address': ipmi_address,
                'pm_user': ipmi_username,
                'pm_password': ipmi_password,
                'terminal_port': None}

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
        node = baremetalclient(request).create(**cls.nova_baremetal_format(
            ipmi_address, cpu, ram, local_disk, mac_addresses,
            ipmi_username=None, ipmi_password=None))

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
        # nodes = test_data().ironicclient_nodes.list()
        node = baremetalclient(request).get(uuid)
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
        nodes = Node.list(request, associated=True)
        node = next((n for n in nodes if instance_uuid == n.instance_uuid),
                    None)

        return node

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

        # nodes = test_data().ironicclient_nodes.list()
        nodes = baremetalclient(request).list()
        if associated is not None:
            if associated:
                nodes = [node for node in nodes
                         if node.instance_uuid is not None]
            else:
                nodes = [node for node in nodes
                         if node.instance_uuid is None]

        return [cls(node) for node in nodes]

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
        baremetalclient(request).delete(uuid)
        return

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
        # ports = test_data().ironicclient_ports.list()[:2]

        # return [port.address for port in ports]
        return [interface["address"] for interface in
                self._apiresource.interfaces]

    @cached_property
    def power_state(self):
        """Return a power state of this Node

        :return: power state of this node
        :rtype:  str
        """
        return self._apiresource.task_state

    @cached_property
    def properties(self):
        """Return properties of this Node

        :return: return memory, cpus and local_disk properties
                 of this Node
        :rtype:  dict of str
        """
        return {
            'ram': self._apiresource.memory_mb / 1024.0,
            'cpu': self._apiresource.cpus,
            'local_disk': self._apiresource.local_gb / 1000.0
        }

    @cached_property
    def driver_info(self):
        """Return driver_info this Node

        :return: return pm_address property of this Node
        :rtype:  dict of str
        """
        return {
            'ipmi_address': self._apiresource.pm_address
        }


class Resource(base.APIResourceWrapper):
    _attrs = ('resource_name', 'resource_type', 'resource_status',
              'physical_resource_id')

    def __init__(self, apiresource, **kwargs):
        super(Resource, self).__init__(apiresource)
        if 'request' in kwargs:
            self._request = kwargs['request']
        if 'instance' in kwargs:
            self._instance = kwargs['instance']
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
        resource = heat.resource_get(overcloud.stack.id,
                                     resource_name)
        return cls(resource, request=request)

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
        if self.physical_resource_id:
            return Instance.get(self._request, self.physical_resource_id)
        return None

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
            return Node.get_by_instance_uuid(self._request,
                                             self.physical_resource_id)
        return None


# TODO(Tzu-Mainn Chen): change this to APIResourceWrapper once
# ResourceCategory object exists in tuskar
class ResourceCategory(base.APIDictWrapper):
    _attrs = ('id', 'name', 'description', 'image_id', 'image_name')

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
