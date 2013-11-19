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

import collections
import copy
import datetime
import logging
import random

import django.conf
import django.db.models
from django.utils.translation import ugettext_lazy as _  # noqa
from novaclient.v1_1.contrib import baremetal
from openstack_dashboard.api import base
from openstack_dashboard.api import nova
import requests
from tuskarclient.v1 import client as tuskar_client

from tuskar_ui.cached_property import cached_property  # noqa


LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(django.conf.settings, 'TUSKAR_ENDPOINT_URL')
REMOTE_NOVA_BAREMETAL_CREDS = getattr(django.conf.settings,
                                      'REMOTE_NOVA_BAREMETAL_CREDS',
                                      False)
OVERCLOUD_CREDS = getattr(django.conf.settings, 'OVERCLOUD_CREDS', False)


# FIXME: request isn't used right in the tuskar client right now, but looking
# at other clients, it seems like it will be in the future
def tuskarclient(request):
    c = tuskar_client.Client(TUSKAR_ENDPOINT_URL)
    return c


def baremetalclient(request):
    def create_remote_nova_client_baremetal():
        nc = nova.nova_client.Client(
            REMOTE_NOVA_BAREMETAL_CREDS['user'],
            REMOTE_NOVA_BAREMETAL_CREDS['password'],
            REMOTE_NOVA_BAREMETAL_CREDS['tenant'],
            auth_url=REMOTE_NOVA_BAREMETAL_CREDS['auth_url'],
            bypass_url=REMOTE_NOVA_BAREMETAL_CREDS['bypass_url'],
        )
        return nc

    def create_nova_client_baremetal():
        insecure = getattr(django.conf.settings, 'OPENSTACK_SSL_NO_VERIFY',
                           False)
        nc = nova.nova_client.Client(
            request.user.username,
            request.user.token.id,
            project_id=request.user.tenant_id,
            auth_url=base.url_for(request, 'compute'),
            insecure=insecure,
            http_log_debug=django.conf.settings.DEBUG)
        nc.client.auth_token = request.user.token.id
        nc.client.management_url = base.url_for(request, 'compute')

        return nc

    if REMOTE_NOVA_BAREMETAL_CREDS:
        LOG.debug('remote nova baremetal client connection created')
        nc = create_remote_nova_client_baremetal()
    else:
        LOG.debug('nova baremetal client connection created using token "%s" '
                  'and url "%s"' %
                  (request.user.token.id, base.url_for(request, 'compute')))
        nc = create_nova_client_baremetal()

    return baremetal.BareMetalNodeManager(nc)


def overcloudclient(request):
    c = nova.nova_client.Client(OVERCLOUD_CREDS['user'],
                                OVERCLOUD_CREDS['password'],
                                OVERCLOUD_CREDS['tenant'],
                                auth_url=OVERCLOUD_CREDS['auth_url'])
    return c


class StringIdAPIResourceWrapper(base.APIResourceWrapper):
    # horizon DataTable class expects ids to be string,
    # if it's not string, then comparison in
    # horizon/tables/base.py:get_object_by_id fails.
    # Because of this, ids returned from dummy api are converted to string
    # (luckily django autoconverts strings to integers when passing string to
    # django model id)

    def __init__(self, apiresource, request=None):
        self.request = request
        self._apiresource = apiresource

    # FIXME
    # this is redefined from base.APIResourceWrapper,
    # remove this when tuskarclient returns object instead of dict
    def __getattr__(self, attr):
        if attr in self._attrs:
            if issubclass(self._apiresource.__class__, dict):
                return self._apiresource.get(attr)
            else:
                try:
                    return self._apiresource.__getattribute__(attr)
                except AttributeError:
                    return None
        else:
            raise AttributeError(attr)

    @property
    def id(self):
        return str(self._apiresource.id)

    # FIXME: self.request is required when calling some instance
    # methods (e.g. list_flavors), once we really start using this request
    # param (if ever), a proper request value should be set
    @property
    def request(self):
        return getattr(self, '_request', None)

    @request.setter
    def request(self, value):
        setattr(self, '_request', value)


class Alert(StringIdAPIResourceWrapper):
    """Wrapper for the Alert object returned by the
    dummy model.
    """
    _attrs = ['message', 'time']


class Capacity(StringIdAPIResourceWrapper):
    """Wrapper for the Capacity object returned by the
    dummy model.
    """
    _attrs = ['name', 'value', 'unit']

    # defines a random usage of capacity - API should probably be able to
    # determine usage of capacity based on capacity value and obejct_id
    @cached_property
    def usage(self):
        return random.randint(0, int(self.value))

    # defines a random average of capacity - API should probably be able to
    # determine average of capacity based on capacity value and obejct_id
    @cached_property
    def average(self):
        return random.randint(0, int(self.value))


class BaremetalNode(StringIdAPIResourceWrapper):
    _attrs = ['id', 'pm_address', 'cpus', 'memory_mb', 'service_host',
              'local_gb', 'pm_user', 'instance_uuid']

    @classmethod
    def create(cls, request, **kwargs):
        # The pm_address, pm_user and terminal_port need to be None when
        # empty for the baremetal vm to work.
        # terminal_port needs separate handling because 0 is a valid value.
        terminal_port = kwargs['terminal_port']
        if terminal_port == '':
            terminal_port = None
        baremetal_node = baremetalclient(request).create(
            kwargs['service_host'],
            kwargs['cpus'],
            kwargs['memory_mb'],
            kwargs['local_gb'],
            kwargs['prov_mac_address'],
            kwargs['pm_address'] or None,
            kwargs['pm_user'] or None,
            kwargs['pm_password'],
            terminal_port)
        return cls(baremetal_node)

    @classmethod
    def get(cls, request, baremetal_node_id):
        baremetal_node = cls(baremetalclient(request).get(baremetal_node_id))
        baremetal_node.request = request

        try:
            # Nova instance info will be added to baremetal node attributes
            nova_instance = nova.server_get(request,
                                            baremetal_node.instance_uuid)
        except Exception:
            nova_instance = None
            LOG.debug("Couldn't obtain nova.server_get instance for "
                      "baremetal node %s" % baremetal_node_id)
        if nova_instance:
            # If baremetal is provisioned, there is a nova instance.
            addresses = nova_instance._apiresource.addresses.get('ctlplane')
            if addresses:
                baremetal_node.ip_address_other = ", ".join(
                    [addr['addr'] for addr in addresses])
            baremetal_node.status = nova_instance._apiresource._info[
                'OS-EXT-STS:vm_state']
            baremetal_node.power_management = ""
            if baremetal_node.pm_user:
                baremetal_node.power_management = (
                    baremetal_node.pm_user + "/********")
        else:
            # If baremetal is unprovisioned, there is no nova instance.
            baremetal_node.status = 'unprovisioned'

        # Returning baremetal node containing nova instance info
        return baremetal_node

    @classmethod
    def list(cls, request):
        return [cls(n, request) for n in
                baremetalclient(request).list()]

    @classmethod
    def list_unracked(cls, request):
        try:
            racked_baremetal_node_ids = [
                tuskar_node.nova_baremetal_node_id
                for tuskar_node in TuskarNode.list(request)]
            return [baremetal_node
                    for baremetal_node in BaremetalNode.list(request)
                    if baremetal_node.id not in racked_baremetal_node_ids]
        except requests.ConnectionError:
            return []

    @cached_property
    def tuskar_node(self):
        node = next((tuskar_node
                     for tuskar_node in TuskarNode.list(self.request)
                     if tuskar_node.nova_baremetal_node_id == self.id),
                    None)
        return node

    @property
    def mac_address(self):
        try:
            return self._apiresource.interfaces[0]['address']
        except Exception:
            return None

    @property
    # FIXME: just mock implementation, add proper one
    def running_instances(self):
        return 4

    @property
    # FIXME: just mock implementation, add proper one
    def remaining_capacity(self):
        return 100 - self.running_instances

    @cached_property
    def running_virtual_machines(self):
        if OVERCLOUD_CREDS:
            search_opts = {}
            search_opts['all_tenants'] = True
            return [
                s for s in overcloudclient(
                    self.request).servers.list(True, search_opts)
                if s.hostId == self.id]
        else:
            LOG.debug(
                "OVERCLOUD_CREDS is not set. Can't connect to Overcloud")
            return []


class TuskarNode(StringIdAPIResourceWrapper):
    """Wrapper for the TuskarNode object returned by the dummy model."""

    _attrs = ['id', 'nova_baremetal_node_id']

    @classmethod
    def get(cls, request, tuskar_node_id):
        tuskar_node = cls(tuskarclient(request).nodes.get(tuskar_node_id))
        tuskar_node.request = request
        return tuskar_node

    @classmethod
    def list(cls, request):
        return [cls(n, request) for n in (tuskarclient(request).nodes.list())]

    def remove_from_rack(self, request):
        rack = self.rack
        baremetal_node_ids = [{'id': tuskar_node.nova_baremetal_node_id}
                              for tuskar_node in rack.list_tuskar_nodes
                              if tuskar_node.id != self.id]
        Rack.update(request, rack.id, {'baremetal_nodes': baremetal_node_ids})

    @cached_property
    def rack(self):
        if self.rack_id:
            return Rack.get(self.request, self.rack_id)
        else:
            return None

    @property
    def rack_id(self):
        try:
            return unicode(self._apiresource.rack['id'])
        except AttributeError:
            return None

    @cached_property
    def nova_baremetal_node(self):
        if self.nova_baremetal_node_id:
            return BaremetalNode.get(self.request, self.nova_baremetal_node_id)
        else:
            return None

    def nova_baremetal_node_attribute(self, attr_name):
        key = "_%s" % attr_name
        if not hasattr(self, key):
            if self.nova_baremetal_node:
                value = getattr(self.nova_baremetal_node, attr_name, None)
            else:
                value = None
            setattr(self, key, value)
        return getattr(self, key)

    @property
    def service_host(self):
        return self.nova_baremetal_node_attribute('service_host')

    @property
    def mac_address(self):
        return self.nova_baremetal_node_attribute('mac_address')

    @property
    def ip_address_other(self):
        return self.nova_baremetal_node_attribute('ip_address_other')

    @property
    def pm_address(self):
        return self.nova_baremetal_node_attribute('pm_address')

    @property
    def status(self):
        return self.nova_baremetal_node_attribute('status')

    @property
    def running_virtual_machines(self):
        return self.nova_baremetal_node_attribute('running_virtual_machines')

    @cached_property
    def list_flavors(self):
        # FIXME: just a mock of used instances, add real values
        used_instances = 0

        if not self.rack or not self.rack.resource_class:
            return []
        resource_class = self.rack.resource_class

        added_flavors = tuskarclient(
            self.request).flavors.list(resource_class.id)
        flavors = []
        if added_flavors:
            for flavor in added_flavors:
                flavor_obj = Flavor(flavor)
                #flavor_obj.max_vms = f.max_vms

                # FIXME just a mock of used instances, add real values
                used_instances += 5
                flavor_obj.used_instances = used_instances
                flavors.append(flavor_obj)
        return flavors

    @property
    # FIXME: just mock implementation, add proper one
    def is_provisioned(self):
        return (self.status != "unprovisioned" and self.rack)

    @cached_property
    def alerts(self):
        return []


class Rack(StringIdAPIResourceWrapper):
    """Wrapper for the Rack object  returned by the
    dummy model.
    """

    _attrs = ['id', 'name', 'location', 'subnet', 'nodes', 'state',
              'capacities']

    @classmethod
    def create(cls, request, **kwargs):
        baremetal_node_ids = kwargs.get('baremetal_nodes', [])
        ## FIXME: set nodes here
        rack = tuskarclient(request).racks.create(
            name=kwargs['name'],
            location=kwargs['location'],
            subnet=kwargs['subnet'],
            nodes=baremetal_node_ids,
            resource_class={'id': kwargs['resource_class_id']},
            slots=0)
        return cls(rack)

    @classmethod
    def update(cls, request, rack_id, rack_kwargs):
        rack_args = copy.copy(rack_kwargs)
        # remove rack_id from kwargs (othervise it is duplicated)
        rack_args.pop('rack_id', None)
        ## FIXME: set nodes here
        baremetal_node_ids = rack_args.pop('baremetal_nodes', None)
        if baremetal_node_ids is not None:
            rack_args['nodes'] = baremetal_node_ids
        # correct data mapping for resource_class
        if 'resource_class_id' in rack_args:
            rack_args['resource_class'] = {
                'id': rack_args.pop('resource_class_id', None)}

        rack = tuskarclient(request).racks.update(rack_id, **rack_args)
        return cls(rack)

    @classmethod
    def list(cls, request, only_free_racks=False):
        if only_free_racks:
            return [Rack(r, request) for r in
                    tuskarclient(request).racks.list() if (
                        getattr(r, 'resource_class', None) is None)]
        else:
            return [Rack(r, request) for r in
                    tuskarclient(request).racks.list()]

    @classmethod
    def get(cls, request, rack_id):
        rack = cls(tuskarclient(request).racks.get(rack_id))
        rack.request = request
        return rack

    @classmethod
    def delete(cls, request, rack_id):
        tuskarclient(request).racks.delete(rack_id)

    @property
    def tuskar_node_ids(self):
        """List of unicode ids of tuskar nodes added to rack."""
        return [unicode(tuskar_node['id']) for tuskar_node in self.nodes]

    @cached_property
    def list_tuskar_nodes(self):
        return [TuskarNode.get(self.request, tuskar_node['id'])
                for tuskar_node in self.nodes]

    @cached_property
    def list_baremetal_nodes(self):
        return [tuskar_node.nova_baremetal_node
                for tuskar_node in self.list_tuskar_nodes]

    @property
    def nodes_count(self):
        return len(self.nodes)

    @property
    def resource_class_id(self):
        try:
            return self._apiresource.resource_class['id']
        except AttributeError:
            return None

    @cached_property
    def resource_class(self):
        if self.resource_class_id:
            return ResourceClass.get(self.request, self.resource_class_id)
        else:
            return None

    @cached_property
    def list_capacities(self):
        return [Capacity(c) for c in self.capacities]

    @cached_property
    def vm_capacity(self):
        """Calculate Rack VM Capacity.

        Rack VM Capacity is maximum value from its Resource Class's Flavors
        max_vms (considering flavor sizes are multiples).
        """
        try:
            value = max([flavor.max_vms for flavor in
                         self.resource_class.list_flavors])
        except Exception:
            value = None
        return Capacity({'name': "VM Capacity", 'value': value, 'unit': 'VMs'})

    @cached_property
    def alerts(self):
        return []

    @property
    def aggregated_alerts(self):
        # FIXME: for now return only list of nodes (particular alerts are not
        # used)
        return [tuskar_node for tuskar_node in self.list_tuskar_nodes
                if tuskar_node.alerts]

    @cached_property
    def list_flavors(self):
        # FIXME just a mock of used instances, add real values
        used_instances = 0

        if not self.resource_class:
            return []
        added_flavors = tuskarclient(
            self.request).flavors.list(self.resource_class_id)
        flavors = []
        for flavor in added_flavors:
            flavor_obj = Flavor(flavor)
            #flavor_obj.max_vms = f.max_vms

            # FIXME just a mock of used instances, add real values
            used_instances += 2
            flavor_obj.used_instances = used_instances
            flavors.append(flavor_obj)
        return flavors

    @property
    def all_used_instances(self):
        return [flavor.used_instances for flavor in self.list_flavors]

    @property
    def total_instances(self):
        # FIXME just mock implementation, add proper one
        return sum(self.all_used_instances)

    @property
    def remaining_capacity(self):
        # FIXME just mock implementation, add proper one
        return 100 - self.total_instances

    @property
    def is_provisioned(self):
        return (self.state == 'active') or (self.state == 'error')

    @property
    def is_provisioning(self):
        return (self.state == 'provisioning')

    @classmethod
    def provision_all(cls, request):
        tuskarclient(request).data_centers.provision_all()


class ResourceClass(StringIdAPIResourceWrapper):
    """Wrapper for the ResourceClass object  returned by the
    dummy model.
    """
    _attrs = ['id', 'name', 'service_type', 'image_id', 'racks']

    @classmethod
    def get(cls, request, resource_class_id):
        rc = cls(tuskarclient(request).resource_classes.get(resource_class_id))
        rc.request = request
        return rc

    @classmethod
    def create(self, request, name, service_type, image_id, flavors):
        return ResourceClass(
            tuskarclient(request).resource_classes.create(
                name=name,
                service_type=service_type,
                image_id=image_id,
                flavors=flavors))

    @classmethod
    def list(cls, request):
        return [cls(rc, request) for rc in (
            tuskarclient(request).resource_classes.list())]

    @classmethod
    def update(cls, request, resource_class_id, name, service_type, image_id,
               flavors):
        resource_class = cls(tuskarclient(request).resource_classes.update(
            resource_class_id,
            name=name,
            service_type=service_type,
            image_id=image_id,
            flavors=flavors))

        ## FIXME: flavors have to be updated separately, seems less than ideal
        for flavor_id in resource_class.flavors_ids:
            Flavor.delete(request, resource_class_id=resource_class.id,
                          flavor_id=flavor_id)
        for flavor in flavors:
            Flavor.create(request,
                          resource_class_id=resource_class.id,
                          **flavor)

        return resource_class

    @property
    def deletable(self):
        return (len(self.racks) <= 0)

    @classmethod
    def delete(cls, request, resource_class_id):
        tuskarclient(request).resource_classes.delete(resource_class_id)

    @property
    def racks_ids(self):
        """List of unicode ids of racks added to resource class."""
        return [unicode(rack['id']) for rack in self.racks]

    @cached_property
    def list_racks(self):
        """List of racks added to ResourceClass."""
        return [Rack.get(self.request, rid) for rid in self.racks_ids]

    def set_racks(self, request, racks_ids):
        # FIXME: there is a bug now in tuskar, we have to remove all racks at
        # first and then add new ones:
        # https://github.com/tuskar/tuskar/issues/37
        tuskarclient(request).resource_classes.update(self.id, racks=[])
        racks = [{'id': rid} for rid in racks_ids]
        tuskarclient(request).resource_classes.update(self.id, racks=racks)

    @property
    def racks_count(self):
        return len(self.racks)

    @cached_property
    def all_racks(self):
        """List all racks suitable for the add/remove dialog.

        List of racks added to ResourceClass + list of free racks,
        meaning racks that don't belong to any ResourceClass.
        """
        return [rack for rack in Rack.list(self.request)
                if rack.resource_class_id is None or
                str(rack.resource_class_id) == self.id]

    @cached_property
    def tuskar_nodes(self):
        return [tuskar_node for tuskar_node in TuskarNode.list(self.request)
                if tuskar_node.rack_id in self.racks_ids]

    @property
    def nodes_count(self):
        return len(self.tuskar_nodes)

    @property
    def flavors_ids(self):
        """List of unicode ids of flavors added to resource class."""
        return [unicode(flavor.id) for flavor in self.list_flavors]

    @cached_property
    def list_flavors(self):
        # FIXME just a mock of used instances, add real values
        used_instances = 0

        added_flavors = tuskarclient(self.request).flavors.list(self.id)
        flavors = []
        for flavor in added_flavors:
            flavor_obj = Flavor(flavor, self.request)
            #flavor_obj.max_vms = f.max_vms

            # FIXME just a mock of used instances, add real values
            used_instances += 5
            flavor_obj.used_instances = used_instances
            flavors.append(flavor_obj)
        return flavors

    @property
    def all_used_instances(self):
        return [flavor.used_instances for flavor in self.list_flavors]

    @property
    def total_instances(self):
        # FIXME just mock implementation, add proper one
        return sum(self.all_used_instances)

    @property
    def remaining_capacity(self):
        # FIXME just mock implementation, add proper one
        return 100 - self.total_instances

    @cached_property
    def capacities(self):
        """Aggregates Rack capacities values."""

        def add_capacities(c1, c2):
            return [Capacity({
                'name': a.name,
                'value': int(a.value) + int(b.value),
                'unit': a.unit,
            }) for a, b in zip(c1, c2)]

        capacities = [rack.list_capacities for rack in self.list_racks]
        return reduce(add_capacities, capacities)

    @cached_property
    def vm_capacity(self):
        """Calculate Class VM Capacity.

        Resource Class VM Capacity is maximum value from its Flavors max_vms
        (considering flavor sizes are multiples), multipled by number of Racks
        in Resource Class.
        """
        try:
            value = self.racks_count * max([flavor.max_vms
                                            for flavor in self.list_flavors])
        except Exception:
            value = _("Unable to retrieve vm capacity")
        return Capacity({
            'name': _("VM Capacity"),
            'value': value,
            'unit': _('VMs'),
        })

    @property
    def aggregated_alerts(self):
        # FIXME: for now return only list of racks (particular alerts are not
        # used)
        return [rack
                for rack in self.list_racks
                if rack.alerts + rack.aggregated_alerts]

    @property
    def has_provisioned_rack(self):
        return any([rack.is_provisioned for rack in self.list_racks])


class Flavor(StringIdAPIResourceWrapper):
    """Wrapper for the Flavor object returned by Tuskar.
    """
    _attrs = ['id', 'name', 'max_vms']

    @classmethod
    def get(cls, request, resource_class_id, flavor_id):
        flavor = cls(tuskarclient(request).flavors.get(resource_class_id,
                                                       flavor_id))
        flavor.request = request
        return flavor

    @classmethod
    def create(cls, request, **kwargs):
        return cls(tuskarclient(request).flavors.create(
            kwargs['resource_class_id'],
            name=kwargs['name'],
            max_vms=kwargs['max_vms'],
            capacities=kwargs['capacities']))

    @classmethod
    def delete(cls, request, **kwargs):
        tuskarclient(request).flavors.delete(
            kwargs['resource_class_id'],
            kwargs['flavor_id'])

    @cached_property
    def capacities(self):
        # FIXME: should we distinguish between tuskar capacities and our
        # internal capacities?
        CapacityStruct = collections.namedtuple(
            'CapacityStruct', 'name value unit')
        return [Capacity(CapacityStruct(c['name'], c['value'], c['unit']))
                for c in self._apiresource.capacities]

    def capacity(self, capacity_name):
        key = "_%s" % capacity_name
        if not hasattr(self, key):
            try:
                capacity = [c for c in self.capacities if (
                    c.name == capacity_name)][0]
            except Exception:
                # FIXME: test this
                capacity = Capacity(
                    name=capacity_name,
                    value=_('Unable to retrieve '
                            '(Is the flavor configured properly?)'),
                    unit='')
            setattr(self, key, capacity)
        return getattr(self, key)

    @property
    def cpu(self):
        return self.capacity('cpu')

    @property
    def memory(self):
        return self.capacity('memory')

    @property
    def storage(self):
        return self.capacity('storage')

    @property
    def ephemeral_disk(self):
        return self.capacity('ephemeral_disk')

    @property
    def swap_disk(self):
        return self.capacity('swap_disk')

    @property
    def running_virtual_machines(self):
        # FIXME: arbitrary number
        return random.randint(0, int(self.cpu.value))

    # defines a random average of capacity - API should probably be able to
    # determine average of capacity based on capacity value and obejct_id
    def vms_over_time(self, start_time, end_time):
        values = []
        current_time = start_time
        while current_time <= end_time:
            values.append(
                {'date': current_time,
                 'value': random.randint(0, self.running_virtual_machines)})
            current_time += datetime.timedelta(hours=1)

        return values
