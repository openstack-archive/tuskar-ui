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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from horizon.utils import memoized
from ironic_discoverd import client as discoverd_client
from ironicclient import client as ironic_client
from openstack_dashboard.api import base
from openstack_dashboard.api import glance
from openstack_dashboard.api import nova
import requests

from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.utils import utils


# power states
ERROR_STATES = set(['deploy failed', 'error'])
POWER_ON_STATES = set(['on', 'power on'])

# provision_states of ironic aggregated to reasonable groups
PROVISION_STATE_FREE = ['available', 'deleted', None]
PROVISION_STATE_PROVISIONED = ['active']
PROVISION_STATE_PROVISIONING = [
    'deploying', 'wait call-back', 'rebuild', 'deploy complete']
PROVISION_STATE_DELETING = ['deleting']
PROVISION_STATE_ERROR = ['error', 'deploy failed']

# names for states of ironic used in UI,
# provison_states + discovery states
DISCOVERING_STATE = 'discovering'
DISCOVERED_STATE = 'discovered'
DISCOVERY_FAILED_STATE = 'discovery failed'
MAINTENANCE_STATE = 'manageable'
PROVISIONED_STATE = 'provisioned'
PROVISIONING_FAILED_STATE = 'provisioning failed'
PROVISIONING_STATE = 'provisioning'
DELETING_STATE = 'deleting'
FREE_STATE = 'free'


IRONIC_DISCOVERD_URL = getattr(settings, 'IRONIC_DISCOVERD_URL', None)
LOG = logging.getLogger(__name__)

@memoized.memoized
def ironicclient(request):
    api_version = 1
    kwargs = {'os_auth_token': request.user.token.id,
              'ironic_url': base.url_for(request, 'baremetal')}
    return ironic_client.get_client(api_version, **kwargs)


# FIXME(lsmola) This should be done in Horizon, they don't have caching
@memoized.memoized
@handle_errors(_("Unable to retrieve image."))
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


class Node(base.APIResourceWrapper):
    _attrs = ('id', 'uuid', 'instance_uuid', 'driver', 'driver_info',
              'properties', 'power_state', 'target_power_state',
              'provision_state', 'maintenance', 'extra')

    def __init__(self, apiresource, request=None, instance=None):
        """Initialize a Node

        :param apiresource: apiresource we want to wrap
        :type  apiresource: IronicNode

        :param request: request
        :type  request: django.core.handlers.wsgi.WSGIRequest

        :param instance: instance relation we want to cache
        :type  instance: openstack_dashboard.api.nova.Server

        :return: Node object
        :rtype:  tusar_ui.api.node.Node
        """
        super(Node, self).__init__(apiresource)
        self._request = request
        self._instance = instance

    @classmethod
    def create(cls, request, ipmi_address=None, cpu_arch=None, cpus=None,
               memory_mb=None, local_gb=None, mac_addresses=[],
               ipmi_username=None, ipmi_password=None, ssh_address=None,
               ssh_username=None, ssh_key_contents=None,
               deployment_kernel=None, deployment_ramdisk=None,
               driver=None):
        """Create a Node in Ironic."""
        if driver == 'pxe_ssh':
            driver_info = {
                'ssh_address': ssh_address,
                'ssh_username': ssh_username,
                'ssh_key_contents': ssh_key_contents,
                'ssh_virt_type': 'virsh',
            }
        else:
            driver_info = {
                'ipmi_address': ipmi_address,
                'ipmi_username': ipmi_username,
                'ipmi_password': ipmi_password
            }
        driver_info.update(
            deploy_kernel=deployment_kernel,
            deploy_ramdisk=deployment_ramdisk
        )

        properties = {'capabilities': 'boot_option:local', }
        if cpus:
            properties.update(cpus=cpus)
        if memory_mb:
            properties.update(memory_mb=memory_mb)
        if local_gb:
            properties.update(local_gb=local_gb)
        if cpu_arch:
            properties.update(cpu_arch=cpu_arch)

        node = ironicclient(request).node.create(
            driver=driver,
            driver_info=driver_info,
            properties=properties,
        )
        for mac_address in mac_addresses:
            ironicclient(request).port.create(
                node_uuid=node.uuid,
                address=mac_address
            )

        return cls(node, request)

    @classmethod
    @memoized.memoized
    @handle_errors(_("Unable to retrieve node"))
    def get(cls, request, uuid):
        """Return the Node that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of Node to be retrieved
        :type  uuid: str

        :return: matching Node, or None if no IronicNode matches the ID
        :rtype:  tuskar_ui.api.node.Node
        """
        node = ironicclient(request).node.get(uuid)
        if node.instance_uuid is not None:
            server = nova.server_get(request, node.instance_uuid)
        else:
            server = None
        return cls(node, request, server)

    @classmethod
    @handle_errors(_("Unable to retrieve node"))
    def get_by_instance_uuid(cls, request, instance_uuid):
        """Return the Node associated with the instance ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param instance_uuid: ID of Instance that is deployed on the Node
                              to be retrieved
        :type  instance_uuid: str

        :return: matching Node
        :rtype:  tuskar_ui.api.node.Node

        :raises: ironicclient.exc.HTTPNotFound if there is no Node with
                 the matching instance UUID
        """
        node = ironicclient(request).node.get_by_instance_uuid(instance_uuid)
        server = nova.server_get(request, instance_uuid)
        return cls(node, request, server)

    @classmethod
    @memoized.memoized
    @handle_errors(_("Unable to retrieve nodes"), [])
    def list(cls, request, associated=None, maintenance=None):
        """Return a list of Nodes

        :param request: request object
        :type  request: django.http.HttpRequest

        :param associated: should we also retrieve all Nodes, only those
                           associated with an Instance, or only those not
                           associated with an Instance?
        :type  associated: bool

        :param maintenance: should we also retrieve all Nodes, only those
                            in maintenance mode, or those which are not in
                            maintenance mode?
        :type  maintenance: bool

        :return: list of Nodes, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.node.Node
        """
        nodes = ironicclient(request).node.list(associated=associated,
                                                maintenance=maintenance)
        if associated is None or associated:
            servers = nova.server_list(request)[0]
            servers_dict = utils.list_to_dict(servers)
            nodes_with_instance = []
            for n in nodes:
                server = servers_dict.get(n.instance_uuid, None)
                nodes_with_instance.append(cls(n, instance=server,
                                               request=request))
            return [cls.get(request, node.uuid)
                    for node in nodes_with_instance]
        return [cls.get(request, node.uuid) for node in nodes]

    @classmethod
    def delete(cls, request, uuid):
        """Delete an Node

        Remove the IronicNode matching the ID if it
        exists; otherwise, does nothing.

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of IronicNode to be removed
        :type  uuid: str
        """
        return ironicclient(request).node.delete(uuid)

    @classmethod
    def discover(cls, request, uuids):
        """Set the maintenance status of node

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuids: IDs of IronicNodes
        :type  uuids: list of str
        """
        if not IRONIC_DISCOVERD_URL:
            return
        for uuid in uuids:
            discoverd_client.introspect(uuid, IRONIC_DISCOVERD_URL,
                                        request.user.token.id)

    @classmethod
    def set_maintenance(cls, request, uuid, maintenance):
        """Set the maintenance status of node

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of Node to be removed
        :type  uuid: str

        :param maintenance: desired maintenance state
        :type  maintenance: bool
        """
        patch = {
            'op': 'replace',
            'value': 'True' if maintenance else 'False',
            'path': '/maintenance'
        }
        node = ironicclient(request).node.update(uuid, [patch])
        return cls(node, request)

    @classmethod
    def set_power_state(cls, request, uuid, power_state):
        """Set the power_state of node

        :param request: request object
        :type  request: django.http.HttpRequest

        :param uuid: ID of Node
        :type  uuid: str

        :param power_state: desired power_state
        :type  power_state: str
        """
        node = ironicclient(request).node.set_power_state(uuid, power_state)
        return cls(node, request)

    @classmethod
    @memoized.memoized
    def list_ports(cls, request, uuid):
        """Return a list of ports associated with this Node

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
        ports = self.list_ports(self._request, self.uuid)
        return [port.address for port in ports]

    @cached_property
    def cpus(self):
        return self.properties.get('cpus', None)

    @cached_property
    def memory_mb(self):
        return self.properties.get('memory_mb', None)

    @cached_property
    def local_gb(self):
        return self.properties.get('local_gb', None)

    @cached_property
    def cpu_arch(self):
        return self.properties.get('cpu_arch', None)

    @cached_property
    def state(self):
        if self.maintenance:
            if not IRONIC_DISCOVERD_URL:
                return MAINTENANCE_STATE
            try:
                status = discoverd_client.get_status(
                    uuid=self.uuid,
                    base_url=IRONIC_DISCOVERD_URL,
                    auth_token=self._request.user.token.id,
                )
            except requests.HTTPError as e:
                if getattr(e.response, 'status_code', None) == 404:
                    return MAINTENANCE_STATE
                raise
            if status['error']:
                return DISCOVERY_FAILED_STATE
            elif status['finished']:
                return DISCOVERED_STATE
            else:
                return DISCOVERING_STATE
        else:
            if self.provision_state in PROVISION_STATE_FREE:
                return FREE_STATE
            if self.provision_state in PROVISION_STATE_PROVISIONING:
                return PROVISIONING_STATE
            if self.provision_state in PROVISION_STATE_PROVISIONED:
                return PROVISIONED_STATE
            if self.provision_state in PROVISION_STATE_DELETING:
                return DELETING_STATE
            if self.provision_state in PROVISION_STATE_ERROR:
                return PROVISIONING_FAILED_STATE
        # Unknown state
        return None

    @cached_property
    def instance(self):
        """Return the Nova Instance associated with this Node

        :return: Nova Instance associated with this Node; or
                 None if there is no Instance associated with this
                 Node, or no matching Instance is found
        :rtype:  Instance
        """
        if self._instance is not None:
            return self._instance
        if self.instance_uuid:
            servers, _has_more_data = nova.server_list(self._request)
            for server in servers:
                if server.id == self.instance_uuid:
                    return server

    @cached_property
    def ip_address(self):
        try:
            apiresource = self.instace._apiresource
        except AttributeError:
            LOG.error("Couldn't obtain IP address")
            return None
        return apiresource.addresses['ctlplane'][0]['addr']

    @cached_property
    def image_name(self):
        """Return image name of associated instance

        Returns image name of instance associated with node

        :return: Image name of instance
        :rtype:  string
        """
        if self.instance is None:
            return
        image = image_get(self._request, self.instance.image['id'])
        return image.name

    @cached_property
    def instance_status(self):
        return getattr(getattr(self, 'instance', None), 'status', None)

    @cached_property
    def provisioning_status(self):
        if self.instance_uuid:
            return _("Provisioned")
        return _("Free")

    @classmethod
    def get_all_mac_addresses(cls, request):
        macs = [node.addresses for node in cls.list(request)]
        return set([mac.upper() for sublist in macs for mac in sublist])
