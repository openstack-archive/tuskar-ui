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


# TODO(Tzu-Mainn Chen): change this to APIResourceWrapper once
# ResourceCategory object exists in tuskar
class Overcloud(base.APIDictWrapper):
    _attrs = ('id', 'stack_id', 'name', 'description')

    @classmethod
    def create(cls, request, overcloud_sizing):
        # Assumptions:
        #   * hard-coded stack name ('overcloud')
        #   * there is a Tuskar API/library that puts
        #     together the Heat template
        # Questions:
        #   * is the assumption correct, or does the UI have to
        #     do more heavy lifting?
        # Required:
        #   * Overcloud sizing information
        # Side Effects:
        #   * call out to Tuskar API/library, which deploys
        #     an 'overcloud' stack using the sizing information
        # Return:
        #   * the created stack object

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # overcloud = tuskarclient(request).overclouds.create(
        #                          'overcloud',
        #                          overcloud_sizing)
        overcloud = test_data().tuskarclient_overclouds.first()

        return cls(overcloud)

    @classmethod
    def list(cls, request):
        # Return:
        #   * a list of Overclouds in Tuskar

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # ocs = tuskarclient(request).overclouds.list()
        ocs = test_data().tuskarclient_overclouds.list()

        return [cls(oc) for oc in ocs]

    @classmethod
    def get(cls, request, overcloud_id):
        # Required:
        #   * overcloud_id
        # Return:
        #   * the 'overcloud' stack object

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # overcloud = tuskarclient(request).overclouds.get(overcloud_id)
        overcloud = test_data().tuskarclient_overclouds.first()

        return cls(overcloud)

    @cached_property
    def stack(self, request):
        # Return:
        #   * the Heat stack associated with this overcoud

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # stack = heatclient(request).stacks.get(self.stack_id)
        stack = test_data().heatclient_stacks.first()
        return stack

    @cached_property
    def is_deployed(self):
        # Assumptions:
        #   * hard-coded stack name ('overcloud')
        # Return:
        #   * True if the overcloud deployed successfully
        #   * False otherwise
        # TODO(rdopieralski) Actually implement it
        return False

    def resources(self, resource_category):
        # Required:
        #   * resource_category
        # Return:
        #   * the resources within the overclod that match the
        #     resource category

        # TODO(Tzu-Mainn Chen): uncomment when possible
        #resources = tuskarclient(request).overclouds.get_resources(
        #    self.id, resource_category.id)

        return [r for r in test_data().heatclient_resources.list()
                if r.logical_resource_id == resource_category.name]

    def instances(self, resource_category):
        # Required:
        #   * resource_category
        # Return:
        #   * the instances corresponding to the resources within the
        #     overcloud that match the resource category

        return [Instance.get(None, r.physical_resource_id) for r
                in self.resources(resource_category)]


class Instance(base.APIResourceWrapper):
    _attrs = ('id', 'name', 'image', 'status')

    @classmethod
    def get(cls, request, instance_id):
        # Required:
        #   * instance_id
        # Return:
        #   * the Server associated with the instace_id

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # instance = novaclient(request).servers.get(instance_id)
        servers = test_data().novaclient_servers.list()
        server = next((s for s in servers if instance_id == s.id),
                      None)

        return cls(server)

    @cached_property
    def node(self):
        return Node.get_by_instance_uuid(None, self.id)


class Node(base.APIResourceWrapper):
    _attrs = ('uuid', 'instance_uuid', 'driver', 'driver_info',
              'properties', 'power_state')

    @classmethod
    def create(cls, request, ipmi_address, cpu, ram, local_disk,
               mac_addresses, ipmi_username=None, ipm_password=None):
        # Questions:
        #   * what parameters can we pass in?
        # Required:
        #   * ipmi_address, cpu, ram (GB), local_disk (TB), mac_address
        # Optional:
        #   * ipmi_username, ipmi_password
        # Side Effects:
        #   * call out to Ironic to registers a Node with the given
        #     parameters.  Create ports as needed.
        # Return:
        #   * the registered Node

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
        # Required:
        #   * uuid
        # Return:
        #   * the Node associated with the uuid

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # node = ironicclient(request).nodes.get(uuid)
        nodes = test_data().ironicclient_nodes.list()
        node = next((n for n in nodes if uuid == n.uuid),
                    None)

        return cls(node)

    @classmethod
    def get_by_instance_uuid(cls, request, instance_uuid):
        # Required:
        #   * instance_uuid
        # Return:
        #   * the Node associated with the instance_uuid

        # TODO(Tzu-Mainn Chen): remove test data when possible
        #node = ironicclient(request).nodes.get_by_instance_uuid(
        #    instance_uuid)
        nodes = test_data().ironicclient_nodes.list()
        node = next((n for n in nodes if instance_uuid == n.instance_uuid),
                    None)

        return cls(node)

    @classmethod
    def list(cls, request, associated=None):
        # Optional:
        #   * free
        # Return:
        #   * a list of Nodes registered in Ironic.

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

    @classmethod
    def delete(cls, request, uuid):
        # Required:
        #   * uuid
        # Side Effects:
        #   * remove the Node with the associated uuid from
        #     Ironic

        # TODO(Tzu-Mainn Chen): uncomment when possible
        # ironicclient(request).nodes.delete(uuid)
        return

    @cached_property
    def resource(self, overcloud):
        # Questions:
        #   * can we assume one resource per Node?
        # Required:
        #   * overcloud
        # Return:
        #   * return the node's associated Resource within the passed-in
        #     overcloud, if any

        return next((r for r in overcloud.resources
                    if r.physical_resource_id == self.instance_uuid),
                    None)

    @cached_property
    def addresses(self):
        # Return:
        #   * return a list of the node's port addresses

        # TODO(Tzu-Mainn Chen): uncomment when possible
        # ports = self.list_ports()
        ports = test_data().ironicclient_ports.list()[:2]

        return [port.address for port in ports]


class Resource(base.APIResourceWrapper):
    _attrs = ('resource_name', 'resource_type', 'resource_status',
              'physical_resource_id')

    @classmethod
    def get(cls, request, overcloud, resource_name):
        # Required:
        #   * overcloud, resource_name
        # Return:
        #   * the matching Resource in the overcloud

        # TODO(Tzu-Mainn Chen): uncomment when possible
        # resource = heatclient(request).resources.get(
        #     overcloud.id,
        #     resource_name)
        resources = test_data().heatclient_resources.list()
        resource = next((r for r in resources
                         if overcloud.id == r.stack_id
                         and resource_name == r.resource_name),
                        None)

        return cls(resource)

    @cached_property
    def node(self):
        # Return:
        #   * return resource's associated Node

        return next((n for n in Node.list
                     if self.physical_resource_id == n.instance_uuid),
                    None)


# TODO(Tzu-Mainn Chen): change this to APIResourceWrapper once
# ResourceCategory object exists in tuskar
class ResourceCategory(base.APIDictWrapper):
    _attrs = ('id', 'name', 'description', 'image_id')

    @classmethod
    def list(cls, request):
        # Return:
        #   * a list of Resource Categories in Tuskar.

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # categories = tuskarclient(request).resource_categories.list()
        rcs = test_data().tuskarclient_resource_categories.list()
        return [cls(rc) for rc in rcs]

    @classmethod
    def get(cls, request, category_id):
        # Required:
        #   * category_id
        # Return:
        #   * the 'resource_category' stack object

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # category = tuskarclient(request).resource_categories.get(category_id)
        categories = ResourceCategory.list(request)
        category = next((c for c in categories if category_id == str(c.id)),
                        None)

        return cls(category)

    @cached_property
    def image(self):
        # Return:
        #   * the image name associated with the ResourceCategory

        # TODO(Tzu-Mainn Chen): remove test data when possible
        # image = glanceclient(request).images.get(self.image_id)
        images = test_data().glanceclient_images.list()
        image = next((i for i in images if self.image_id == i.id),
                     None)

        return image
