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
import django.conf
import heatclient
import logging

from django.utils.translation import ugettext_lazy as _
from horizon.utils import memoized
from novaclient.v1_1.contrib import baremetal
from openstack_dashboard.api import base
from openstack_dashboard.api import glance
from openstack_dashboard.api import heat
from openstack_dashboard.api import nova
from openstack_dashboard.test.test_data import utils
from tuskarclient.v1 import client as tuskar_client

from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.test.test_data import tuskar_data

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


# FIXME(lsmola) This should be done in Horizon, they don't have caching
@memoized.memoized
def image_get(request, image_id):
    """Returns an Image object with metadata

    Returns an Image object populated with metadata for image
    with supplied identifier.

    :param image_id: list of objects to be put into a dict
    :type  object_list: list

    :return: object
    :rtype: glanceclient.v1.images.Image
    """
    image = glance.image_get(request, image_id)
    return image


class NodeProfile(object):

    def __init__(self, flavor):
        """Construct node profile by wrapping flavor

        :param flavor: Nova flavor
        :type  flavor: novaclient.v1_1.flavors.Flavor
        """
        self._flavor = flavor

    def __getattr__(self, name):
        return getattr(self._flavor, name)

    @cached_property
    def extras_dict(self):
        """Return extra parameters of node profile

        :return: Nova flavor keys
        :rtype: dict
        """
        return self._flavor.get_keys()

    @property
    def cpu_arch(self):
        return self.extras_dict.get('cpu_arch', '')

    @property
    def kernel_image_id(self):
        return self.extras_dict.get('baremetal:deploy_kernel_id', '')

    @property
    def ramdisk_image_id(self):
        return self.extras_dict.get('baremetal:deploy_ramdisk_id', '')

    @classmethod
    def create(cls, request, name, memory, vcpus, disk, cpu_arch,
               kernel_image_id, ramdisk_image_id):
        extras_dict = {'cpu_arch': cpu_arch,
                       'baremetal:deploy_kernel_id': kernel_image_id,
                       'baremetal:deploy_ramdisk_id': ramdisk_image_id}
        return cls(nova.flavor_create(request, name, memory, vcpus, disk,
                                      metadata=extras_dict))

    @classmethod
    def get(cls, request, node_profile_id):
        return cls(nova.flavor_get(request, node_profile_id))

    @classmethod
    @handle_errors(_("Unable to retrieve node profile list."), [])
    def list(cls, request):
        return [cls(item) for item in nova.flavor_list(request)]

    @classmethod
    @memoized.memoized
    @handle_errors(_("Unable to retrieve existing servers list."), [])
    def list_deployed_ids(cls, request):
        """Get and memoize ID's of deployed node profiles."""
        servers = nova.server_list(request)[0]
        return set(server.flavor['id'] for server in servers)


class Overcloud(base.APIResourceWrapper):
    _attrs = ('id', 'stack_id', 'name', 'description', 'counts', 'attributes')

    def __init__(self, apiresource, request=None):
        super(Overcloud, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, overcloud_sizing, overcloud_configuration):
        """Create an Overcloud in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_sizing: overcloud sizing information with structure
                                 {('overcloud_role_id',
                                   'flavor_name'): count, ...}
        :type  overcloud_sizing: dict

        :param overcloud_configuration: overcloud configuration with structure
                                        {'key': 'value', ...}
        :type  overcloud_configuration: dict

        :return: the created Overcloud object
        :rtype:  tuskar_ui.api.Overcloud
        """
        # TODO(lsmola) for now we have to transform the sizing to simpler
        # format, till API will accept the more complex with flavors,
        # then we delete this
        transformed_sizing = [{
            'overcloud_role_id': role,
            'num_nodes': sizing,
        } for (role, flavor), sizing in overcloud_sizing.items()]

        overcloud = tuskarclient(request).overclouds.create(
            name='overcloud', description="Openstack cloud providing VMs",
            counts=transformed_sizing, attributes=overcloud_configuration)

        return cls(overcloud, request=request)

    @classmethod
    def list(cls, request):
        """Return a list of Overclouds in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Overclouds, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Overcloud
        """
        ocs = tuskarclient(request).overclouds.list()

        return [cls(oc, request=request) for oc in ocs]

    @classmethod
    @handle_errors(_("Unable to retrieve deployment"))
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
        # FIXME(lsmola) hack for Icehouse, only one Overcloud is allowed
        # TODO(lsmola) uncomment when possible
        # overcloud = tuskarclient(request).overclouds.get(overcloud_id)
        # return cls(overcloud, request=request)
        return cls.get_the_overcloud(request)

    # TODO(lsmola) before will will support multiple overclouds, we
    # can work only with overcloud that is named overcloud. Delete
    # this once we have more overclouds. Till then, this is the overcloud
    # that rules them all.
    # This is how API supports it now, so we have to have it this way.
    # Also till Overcloud workflow is done properly, we have to work
    # with situations that overcloud is deleted, but stack is still
    # there. So overcloud will pretend to exist when stack exist.
    @classmethod
    def get_the_overcloud(cls, request):
        overcloud_list = cls.list(request)
        for overcloud in overcloud_list:
            if overcloud.name == 'overcloud':
                return overcloud

        the_overcloud = cls(object(), request=request)
        # I need to mock attributes of overcloud that is being deleted.
        the_overcloud.id = "deleting_in_progress"

        if the_overcloud.stack and the_overcloud.is_deleting:
            return the_overcloud
        else:
            raise heatclient.exc.HTTPNotFound()

    @classmethod
    def delete(cls, request, overcloud_id):
        """Create an Overcloud in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_id: overcloud id
        :type  overcloud_id: int
        """
        tuskarclient(request).overclouds.delete(overcloud_id)

    @cached_property
    def stack(self):
        """Return the Heat Stack associated with this Overcloud

        :return: Heat Stack associated with this Overcloud; or None
                 if no Stack is associated, or no Stack can be
                 found
        :rtype:  heatclient.v1.stacks.Stack or None
        """
        # TODO(lsmola) load it properly, once the API has finished workflow
        # and for example there can't be a situation when I delete Overcloud
        # but Stack is still deleting. So the Overcloud will represent the
        # state of all inner entities and operations correctly.
        # Then also delete the try/except, it should not be caught on this
        # level.
        return heat.stack_get(self._request, 'overcloud')

    @cached_property
    def stack_events(self):
        """Return the Heat Events associated with this Overcloud

        :return: list of Heat Events associated with this Overcloud;
                 or an empty list if there is no Stack associated with
                 this Overcloud, or there are no Events
        :rtype:  list of heatclient.v1.events.Event
        """
        if self.stack:
            return heat.events_list(self._request,
                                    self.stack.stack_name)
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

    @cached_property
    def is_deploying(self):
        """Check if this Overcloud is currently deploying or updating.

        :return: True if deployment is in progress, False otherwise.
        :rtype: bool
        """
        return self.stack.stack_status in ('CREATE_IN_PROGRESS',
                                           'UPDATE_IN_PROGRESS')

    @cached_property
    def is_failed(self):
        """Check if this Overcloud failed to update or deploy.

        :return: True if deployment there was an error, False otherwise.
        :rtype: bool
        """
        return self.stack.stack_status in ('CREATE_FAILED',
                                           'UPDATE_FAILED')

    @cached_property
    def is_deleting(self):
        """Check if this Overcloud is deleting.

        :return: True if Overcloud is deleting, False otherwise.
        :rtype: bool
        """
        return self.stack.stack_status in ('DELETE_IN_PROGRESS', )

    @memoized.memoized
    def all_resources(self, with_joins=True):
        """Return a list of all Overcloud Resources

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Resource?
        :type  with_joins: bool

        :return: list of all Overcloud Resources or an empty list if there
                 are none
        :rtype:  list of tuskar_ui.api.Resource
        """
        # FIXME(lsmola) of this is a temporary hack. When I delete the stack
        # there is a brief moment when list of resources throws an exception
        # a second later, it does not. So the delete in progress page will
        # need to be separated, because it is 'special'. Till then, this hack
        # stays.
        try:
            resources = [r for r in heat.resources_list(self._request,
                                                        self.stack.stack_name)]
        except heatclient.exc.HTTPNotFound:
            resources = []

        if not with_joins:
            return [Resource(r, request=self._request) for r in resources]

        nodes_dict = list_to_dict(Node.list(self._request, associated=True),
                                  key_attribute='instance_uuid')
        joined_resources = []
        for r in resources:
            node = nodes_dict.get(r.physical_resource_id, None)
            joined_resources.append(Resource(r,
                                             node=node,
                                             request=self._request))
        # TODO(lsmola) I want just resources with nova instance
        # this could be probably filtered a better way, investigate
        return [r for r in joined_resources if r.node is not None]

    @memoized.memoized
    def resources(self, overcloud_role, with_joins=True):
        """Return a list of Overcloud Resources that match an Overcloud Role

        :param overcloud_role: role of resources to be returned
        :type  overcloud_role: tuskar_ui.api.OvercloudRole

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Resource?
        :type  with_joins: bool

        :return: list of Overcloud Resources that match the Overcloud Role,
                 or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Resource
        """
        # FIXME(lsmola) with_joins is not necessary here, I need at least
        # nova instance
        all_resources = self.all_resources(with_joins)
        filtered_resources = [resource for resource in all_resources if
                              (resource.node.is_overcloud_role(
                                  overcloud_role))]

        return filtered_resources

    @cached_property
    def dashboard_url(self):
        # TODO(rdopieralski) Implement this.
        return "http://horizon.example.com"


class Node(base.APIResourceWrapper):
    # FIXME(lsmola) uncomment this and delete equivalent methods
    #_attrs = ('uuid', 'instance_uuid', 'driver', 'driver_info',
    #          'properties', 'power_state')
    _attrs = ('id', 'uuid', 'instance_uuid')

    def __init__(self, apiresource, request=None, **kwargs):
        """Initialize a node

        :param apiresource: apiresource we want to wrap
        :type  apiresource: novaclient.v1_1.contrib.baremetal.BareMetalNode

        :param request: request
        :type  request: django.core.handlers.wsgi.WSGIRequest

        :param instance: instance relation we want to cache
        :type  instance: openstack_dashboard.api.nova.Server

        :return: Node object
        :rtype:  Node
        """
        super(Node, self).__init__(apiresource)
        self._request = request
        if 'instance' in kwargs:
            self._instance = kwargs['instance']

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
    @handle_errors(_("Unable to retrieve node"))
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

        node = baremetalclient(request).get(uuid)

        if node.instance_uuid is not None:
            server = nova.server_get(request, node.instance_uuid)
            return cls(node, instance=server, request=request)

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
        # node = ironicclient(request).nodes.get_by_instance_uuid(
        #    instance_uuid)

        server = nova.server_get(request, instance_uuid)
        nodes = baremetalclient(request).list()

        node = next((n for n in nodes if instance_uuid == n.instance_uuid),
                    None)

        return cls(node, instance=server, request=request)

    @classmethod
    @handle_errors(_("Unable to retrieve nodes"), [])
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
                return [cls(node, request=request) for node in nodes]

        servers, has_more_data = nova.server_list(request)

        servers_dict = list_to_dict(servers)
        nodes_with_instance = []
        for n in nodes:
            server = servers_dict.get(n.instance_uuid, None)
            nodes_with_instance.append(cls(n, instance=server,
                                           request=request))

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
        baremetalclient(request).delete(uuid)
        return

    @cached_property
    def instance(self):
        """Return the Nova Instance associated with this Node

        :return: Nova Instance associated with this Node; or
                 None if there is no Instance associated with this
                 Node, or no matching Instance is found
        :rtype:  tuskar_ui.api.Instance
        """
        if hasattr(self, '_instance'):
            return self._instance

        if self.instance_uuid:
            server = nova.server_get(self._request, self.instance_uuid)
            return server

        return None

    @cached_property
    def image_name(self):
        """Return image name of associated instance

        Returns image name of instance associated with node

        :return: Image name of instance
        :rtype:  string
        """
        if self.instance is None:
            return
        return image_get(self._request, self.instance.image['id']).name

    def is_overcloud_role(self, overcloud_role):
        """Determine whether a node matches an overcloud role

        :param overcloud_role: overcloud role to check against
        :type  overcloud_role: tuskar_ui.api.OvercloudRole

        :return: does this node match the overcloud_role?
        :rtype:  bool
        """
        return self.image_name == overcloud_role.image_name

    @cached_property
    def overcloud_role(self):
        """Return overcloud role of associated instance

        :return: OvercloudRole of associated instance, or None if
                 none exists
        :rtype:  tuskar_ui.api.OvercloudRole
        """
        roles = OvercloudRole.list(self._request)
        for role in roles:
            if self.is_overcloud_role(role):
                return role

    @cached_property
    def addresses(self):
        # FIXME(lsmola) remove when Ironic is in
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
        # FIXME(lsmola) remove when Ironic is in
        """Return a power state of this Node

        :return: power state of this node
        :rtype:  str
        """
        task_state = self._apiresource.task_state
        task_state_dict = {
            'active': 'on',
            'reboot': 'rebooting'
        }
        return task_state_dict.get(task_state, 'off')

    @cached_property
    def properties(self):
        # FIXME(lsmola) remove when Ironic is in
        """Return properties of this Node

        :return: return memory, cpus and local_disk properties
                 of this Node, ram and local_disk properties
                 are in bytes
        :rtype:  dict of str
        """
        return {
            'ram': self._apiresource.memory_mb * 1024.0 * 1024.0,
            'cpu': self._apiresource.cpus,
            'local_disk': self._apiresource.local_gb * 1024.0 * 1024.0 * 1024.0
        }

    @cached_property
    def driver_info(self):
        # FIXME(lsmola) remove when Ironic is in
        """Return driver_info for this Node

        :return: return pm_address property of this Node
        :rtype:  dict of str
        """
        # FIXME(lsmola) Ironic doc is missing, so I don't know
        # whether this belongs here
        try:
            ip_address = (self.instance._apiresource.addresses['ctlplane'][0]
                          ['addr'])
        except Exception:
            LOG.error("Couldn't obtain IP address")
            ip_address = None

        return {
            'ipmi_address': self._apiresource.pm_address,
            'ip_address': ip_address
        }

    @cached_property
    def instance_status(self):
        return getattr(getattr(self, 'instance', None),
                       'status', None)


class Resource(base.APIResourceWrapper):
    _attrs = ('resource_name', 'resource_type', 'resource_status',
              'physical_resource_id')

    def __init__(self, apiresource, request=None, **kwargs):
        """Initialize a resource

        :param apiresource: apiresource we want to wrap
        :type  apiresource: heatclient.v1.resources.Resource

        :param request: request
        :type  request: django.core.handlers.wsgi.WSGIRequest

        :param node: node relation we want to cache
        :type  node: tuskar_ui.api.Node

        :return: Resource object
        :rtype:  Resource
        """
        super(Resource, self).__init__(apiresource)
        self._request = request
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


class OvercloudRole(base.APIResourceWrapper):
    _attrs = ('id', 'name', 'description', 'image_name', 'flavor_id')

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud roles"), [])
    def list(cls, request):
        """Return a list of Overcloud Roles in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Overcloud Roles, or an empty list if there
                 are none
        :rtype:  list of tuskar_ui.api.OvercloudRole
        """
        roles = tuskarclient(request).overcloud_roles.list()
        return [cls(role) for role in roles]

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud role"))
    def get(cls, request, role_id):
        """Return the Tuskar OvercloudRole that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param role_id: ID of OvercloudRole to be retrieved
        :type  role_id: int

        :return: matching OvercloudRole, or None if no matching
                 OvercloudRole can be found
        :rtype:  tuskar_ui.api.OvercloudRole
        """
        role = tuskarclient(request).overcloud_roles.get(role_id)
        return cls(role)

    def update(self, request, **kwargs):
        """Update the selected attributes of Tuskar OvercloudRole.

        :param request: request object
        :type  request: django.http.HttpRequest
        """
        for attr in kwargs:
            if attr not in self._attrs:
                raise TypeError('Invalid parameter %r' % attr)
        tuskarclient(request).overcloud_roles.update(self.id, **kwargs)
