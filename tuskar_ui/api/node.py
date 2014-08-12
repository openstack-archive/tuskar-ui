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

from django.utils.translation import ugettext_lazy as _
from horizon.utils import memoized
from ironicclient import client as ironic_client
from novaclient.v1_1.contrib import baremetal
from openstack_dashboard.api import base
from openstack_dashboard.api import glance
from openstack_dashboard.api import nova
from openstack_dashboard.test.test_data import utils as test_utils

from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.test.test_data import heat_data
from tuskar_ui.test.test_data import node_data
from tuskar_ui.utils import utils


TEST_DATA = test_utils.TestDataContainer()
node_data.data(TEST_DATA)
heat_data.data(TEST_DATA)

LOG = logging.getLogger(__name__)


def baremetalclient(request):
    nc = nova.novaclient(request)
    return baremetal.BareMetalNodeManager(nc)


def ironicclient(request):
    api_version = 1
    kwargs = {'os_auth_token': request.user.token.id,
              'ironic_url': base.url_for(request, 'baremetal')}
    return ironic_client.get_client(api_version, **kwargs)


# FIXME(lsmola) This should be done in Horizon, they don't have caching
@memoized.memoized
def image_get(request, image_id):
    """Returns an Image object with metadata

    Returns an Image object populated with metadata for image
    with supplied identifier.

    :param image_id: list of objects to be put into a dict
    :type  image_id: list

    :return: object
    :rtype: glanceclient.v1.images.Image
    """
    image = glance.image_get(request, image_id)
    return image


class IronicNode(base.APIResourceWrapper):
    _attrs = ('id', 'uuid', 'instance_uuid', 'driver', 'driver_info',
              'properties', 'power_state', 'maintenance')

    def __init__(self, apiresource, request=None):
        super(IronicNode, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, ipmi_address, cpu_arch, cpus, memory_mb,
               local_gb, mac_addresses, ipmi_username=None, ipmi_password=None,
               driver=None):
        """Create a Node in Ironic
        """
        node = ironicclient(request).node.create(
            driver=driver,
            driver_info={
                'ipmi_address': ipmi_address,
                'ipmi_username': ipmi_username,
                'password': ipmi_password
            },
            properties={
                'cpus': cpus,
                'memory_mb': memory_mb,
                'local_gb': local_gb,
                'cpu_arch': cpu_arch,
            }
        )
        for mac_address in mac_addresses:
            ironicclient(request).port.create(
                node_uuid=node.uuid,
                address=mac_address
            )

        return cls(node, request)

    @classmethod
    def get(cls, request, uuid):
        """Return the IronicNode that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of IronicNode to be retrieved
        :type  uuid: str

        :return: matching IronicNode, or None if no IronicNode matches the ID
        :rtype:  tuskar_ui.api.node.IronicNode
        """
        node = ironicclient(request).node.get(uuid)
        return cls(node, request)

    @classmethod
    def get_by_instance_uuid(cls, request, instance_uuid):
        """Return the IronicNode associated with the instance ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param instance_uuid: ID of Instance that is deployed on the IronicNode
                              to be retrieved
        :type  instance_uuid: str

        :return: matching IronicNode
        :rtype:  tuskar_ui.api.node.IronicNode

        :raises: ironicclient.exc.HTTPNotFound if there is no IronicNode with
                 the matching instance UUID
        """
        node = ironicclient(request).node.get_by_instance_uuid(instance_uuid)
        return cls(node, request)

    @classmethod
    @handle_errors(_("Unable to retrieve nodes"), [])
    def list(cls, request, associated=None):
        """Return a list of IronicNodes

        :param request: request object
        :type  request: django.http.HttpRequest

        :param associated: should we also retrieve all IronicNodes, only those
                           associated with an Instance, or only those not
                           associated with an Instance?
        :type  associated: bool

        :return: list of IronicNodes, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.node.IronicNode
        """
        nodes = ironicclient(request).node.list(associated=associated)
        return [cls(cls.get(request, node.uuid), request) for node in nodes]

    @classmethod
    @handle_errors(_("Unable to retrieve newly discovered nodes"), [])
    def list_discovered(cls, request):
        """Return a list of IronicNodes which have been newly discovered
        """
        nodes = [node for node in ironicclient(request).node.list()
                 if getattr(node, 'newly_discovered', False)]
        return [cls(cls.get(request, node.uuid), request) for node in nodes]

    @classmethod
    def delete(cls, request, uuid):
        """Remove the IronicNode matching the ID if it
        exists; otherwise, does nothing.

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of IronicNode to be removed
        :type  uuid: str
        """
        return ironicclient(request).node.delete(uuid)

    @classmethod
    def list_ports(cls, request, uuid):
        """Return a list of ports associated with this IronicNode

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of IronicNode
        :type  uuid: str
        """
        return ironicclient(request).node.list_ports(uuid)

    @cached_property
    def addresses(self):
        """Return a list of port addresses associated with this IronicNode

        :return: list of port addresses associated with this IronicNode, or
                 an empty list if no addresses are associated with
                 this IronicNode
        :rtype:  list of str
        """
        ports = IronicNode.list_ports(self._request, self.uuid)
        return [port.address for port in ports]

    @cached_property
    def cpus(self):
        return self.properties['cpus']

    @cached_property
    def memory_mb(self):
        return self.properties['memory_mb']

    @cached_property
    def local_gb(self):
        return self.properties['local_gb']

    @cached_property
    def cpu_arch(self):
        return self.properties['cpu_arch']


class BareMetalNode(base.APIResourceWrapper):
    _attrs = ('id', 'uuid', 'instance_uuid', 'memory_mb', 'cpus', 'local_gb',
              'task_state', 'pm_user', 'pm_address', 'interfaces')

    @classmethod
    def create(cls, request, ipmi_address, cpu_arch, cpus, memory_mb,
               local_gb, mac_addresses, ipmi_username=None, ipmi_password=None,
               driver=None):
        """Create a Nova BareMetalNode
        """
        node = TEST_DATA.baremetalclient_nodes.first()
        return cls(node)

    @classmethod
    def get(cls, request, uuid):
        """Return the BareMetalNode that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of BareMetalNode to be retrieved
        :type  uuid: str

        :return: matching BareMetalNode, or None if no BareMetalNode matches
                 the ID
        :rtype:  tuskar_ui.api.node.BareMetalNode
        """
        for node in BareMetalNode.list(request):
            if node.uuid == uuid:
                return node

    @classmethod
    def get_by_instance_uuid(cls, request, instance_uuid):
        """Return the BareMetalNode associated with the instance ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param instance_uuid: ID of Instance that is deployed on the
                              BareMetalNode to be retrieved
        :type  instance_uuid: str

        :return: matching BareMetalNode
        :rtype:  tuskar_ui.api.node.BareMetalNode

        :raises: ironicclient.exc.HTTPNotFound if there is no BareMetalNode
                 with the matching instance UUID
        """
        for node in BareMetalNode.list(request):
            if node.instance_uuid == instance_uuid:
                return node

    @classmethod
    def list(cls, request, associated=None):
        """Return a list of BareMetalNodes

        :param request: request object
        :type  request: django.http.HttpRequest

        :param associated: should we also retrieve all BareMetalNodes, only
                           those associated with an Instance, or only those not
                           associated with an Instance?
        :type  associated: bool

        :return: list of BareMetalNodes, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.node.BareMetalNode
        """
        nodes = TEST_DATA.baremetalclient_nodes.list()
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
        """Remove the BareMetalNode if it exists; otherwise, do nothing.

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of BareMetalNode to be removed
        :type  uuid: str
        """
        return

    @cached_property
    def power_state(self):
        """Return a power state of this BareMetalNode

        :return: power state of this node
        :rtype:  str
        """
        task_state_dict = {
            'initializing': 'initializing',
            'active': 'on',
            'reboot': 'rebooting',
            'building': 'building',
            'deploying': 'deploying',
            'prepared': 'prepared',
            'deleting': 'deleting',
            'deploy failed': 'deploy failed',
            'deploy complete': 'deploy complete',
            'deleted': 'deleted',
            'error': 'error',
        }
        return task_state_dict.get(self.task_state, 'off')

    @cached_property
    def driver(self):
        """Return driver for this BareMetalNode
        """
        return "IPMI + PXE"

    @cached_property
    def driver_info(self):
        """Return driver_info for this BareMetalNode

        :return: return pm_address property of this BareMetalNode
        :rtype:  dict of str
        """
        # TODO(akrivoka): mocking driver info, remove later
        node = TEST_DATA.baremetalclient_nodes.first()
        return {
            'ipmi_address': node.ipmi_address,
            'ipmi_username': node.ipmi_username,
            'ipmi_password': node.ipmi_password,
            'ip_address': node.ip_address,
        }

        try:
            ip_address = (self.instance._apiresource.addresses['ctlplane'][0]
                          ['addr'])
        except Exception:
            LOG.error("Couldn't obtain IP address")
            ip_address = None

        return {
            'ipmi_username': self.pm_user,
            'ipmi_address': self.pm_address,
            'ip_address': ip_address
        }

    @cached_property
    def addresses(self):
        """Return a list of port addresses associated with this BareMetalNode

        :return: list of port addresses associated with this BareMetalNode, or
                 an empty list if no addresses are associated with
                 this BareMetalNode
        :rtype:  list of str
        """
        return [interface["address"] for interface in
                self.interfaces]


class NodeClient(object):

    def __init__(self, request):
        if self.ironic_enabled(request):
            self.node_class = IronicNode
        else:
            self.node_class = BareMetalNode

    @classmethod
    def ironic_enabled(cls, request):
        return base.is_service_enabled(request, 'baremetal')


class Node(base.APIResourceWrapper):
    _attrs = ('id', 'uuid', 'instance_uuid', 'driver', 'driver_info',
              'power_state', 'addresses', 'maintenance', 'cpus',
              'memory_mb', 'local_gb', 'cpu_arch')

    def __init__(self, apiresource, request=None, **kwargs):
        """Initialize a Node

        :param apiresource: apiresource we want to wrap
        :type  apiresource: novaclient.v1_1.contrib.baremetal.BareMetalNode

        :param request: request
        :type  request: django.core.handlers.wsgi.WSGIRequest

        :param instance: instance relation we want to cache
        :type  instance: openstack_dashboard.api.nova.Server

        :return: Node object
        :rtype:  tusar_ui.api.node.Node
        """
        super(Node, self).__init__(apiresource)
        self._request = request
        if 'instance' in kwargs:
            self._instance = kwargs['instance']

    @classmethod
    def create(cls, request, ipmi_address, cpu_arch, cpus, memory_mb,
               local_gb, mac_addresses, ipmi_username=None, ipmi_password=None,
               driver=None):
        return cls(NodeClient(request).node_class.create(
            request, ipmi_address, cpu_arch, cpus, memory_mb, local_gb,
            mac_addresses, ipmi_username=ipmi_username,
            ipmi_password=ipmi_password, driver=driver))

    @classmethod
    @handle_errors(_("Unable to retrieve node"))
    def get(cls, request, uuid):
        node = NodeClient(request).node_class.get(request, uuid)
        if node.instance_uuid is not None:
            for server in TEST_DATA.novaclient_servers.list():
                if server.id == node.instance_uuid:
                    break
            else:
                server = None
            return cls(node, instance=server, request=request)

        return cls(node)

    @classmethod
    @handle_errors(_("Unable to retrieve node"))
    def get_by_instance_uuid(cls, request, instance_uuid):
        node = NodeClient(request).node_class.get_by_instance_uuid(
            request, instance_uuid)
        for server in TEST_DATA.novaclient_servers.list():
            if server.id == node.instance_uuid:
                break
        else:
            server = None
        return cls(node, instance=server, request=request)

    @classmethod
    @handle_errors(_("Unable to retrieve nodes"), [])
    def list(cls, request, associated=None):
        nodes = NodeClient(request).node_class.list(
            request, associated=associated)
        if associated is None or associated:
            servers = TEST_DATA.novaclient_servers.list()
            servers_dict = utils.list_to_dict(servers)
            nodes_with_instance = []
            for n in nodes:
                server = servers_dict.get(n.instance_uuid, None)
                nodes_with_instance.append(cls(n, instance=server,
                                               request=request))
            return nodes_with_instance
        else:
            return [cls(node, request=request) for node in nodes]

    @classmethod
    @handle_errors(_("Unable to retrieve discovered nodes"), [])
    def list_discovered(cls, request):
        nodes = NodeClient(request).node_class.list_discovered(request)
        return [cls(node, request=request) for node in nodes]

    @classmethod
    def delete(cls, request, uuid):
        NodeClient(request).node_class.delete(request, uuid)

    @cached_property
    def instance(self):
        """Return the Nova Instance associated with this Node

        :return: Nova Instance associated with this Node; or
                 None if there is no Instance associated with this
                 Node, or no matching Instance is found
        :rtype:  Instance
        """
        if self.instance_uuid:
            servers, _has_more_data = nova.server_list(self._request)
            for server in servers:
                if server.id == self.instance_uuid:
                    return server

    @cached_property
    def ip_address(self):
        return (self.instance._apiresource.addresses['ctlplane'][0]
                ['addr'])

    @cached_property
    def image_name(self):
        """Return image name of associated instance

        Returns image name of instance associated with node

        :return: Image name of instance
        :rtype:  string
        """
        if self.instance is None:
            return
        for image in TEST_DATA.glanceclient_images.list():
            if image.id == self.instance.image['id']:
                return image.name

    @cached_property
    def instance_status(self):
        return getattr(getattr(self, 'instance', None),
                       'status', None)

    @cached_property
    def provisioning_status(self):
        if self.instance_uuid:
            return _("Provisioned")
        return _("Free")


def filter_nodes(nodes, healthy=None, power_state=None):
    """Filters the list of Nodes and returns the filtered list.

    :param nodes:   list of tuskar_ui.api.node.Node objects to filter
    :type  nodes:   list
    :param healthy: retrieve all Nodes (healthy=None),
                    only the healthly ones (healthy=True),
                    or only those in an error state (healthy=False)
    :type  healthy: None or bool
    :param power_state: retrieve all Nodes (power_state=None),
                    only those that are running (power_state=True),
                    or only those that are stopped (power_state=False)
    :type  power_state: None or bool
    :return:        list of filtered tuskar_ui.api.node.Node objects
    :rtype:         list
    """
    error_states = ('deploy failed', 'error',)

    if healthy is not None:
        if healthy:
            nodes = [node for node in nodes
                     if node.power_state not in error_states]
        else:
            nodes = [node for node in nodes
                     if node.power_state in error_states]

    if power_state is not None:
        if power_state:
            nodes = [node for node in nodes if node.power_state == 'on']
        else:
            nodes = [node for node in nodes if node.power_state != 'on']

    return nodes
