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

import copy
import logging
import re
from collections import namedtuple
import itertools
from datetime import timedelta
from random import randint

from django.conf import settings
from django.db.models import Sum, Max
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions

from tuskarclient.v1 import client as tuskar_client

from openstack_dashboard.api import base, nova
import openstack_dashboard.dashboards.infrastructure.models as dummymodels


LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(settings, 'TUSKAR_ENDPOINT_URL')
NOVA_BAREMETAL_CREDS = getattr(settings, 'NOVA_BAREMETAL_CREDS')


# FIXME: request isn't used right in the tuskar client right now, but looking
# at other clients, it seems like it will be in the future
def tuskarclient(request):
    c = tuskar_client.Client(TUSKAR_ENDPOINT_URL)
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
                return self._apiresource.__getattribute__(attr)
        else:
            msg = ('Attempted to access unknown attribute "%s" on '
                   'APIResource object of type "%s" wrapping resource of '
                   'type "%s".') % (attr, self.__class__,
                                    self._apiresource.__class__)
            LOG.debug(exceptions.error_color(msg))
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

    @classmethod
    def create(cls, request, content_object, name, value, unit):
        c = dummymodels.Capacity(
            content_object=content_object,
            name=name,
            value=value,
            unit=unit)
        c.save()
        return Capacity(c)

    @classmethod
    def update(cls, request, capacity_id, content_object, name, value, unit):
        c = dummymodels.Capacity.objects.get(id=capacity_id)
        c.content_object = content_object
        c.name = name
        c.value = value
        c.unit = unit
        c.save()
        return cls(c)

    # defines a random usage of capacity - API should probably be able to
    # determine usage of capacity based on capacity value and obejct_id
    @property
    def usage(self):
        if not hasattr(self, '_usage'):
            self._usage = randint(0, int(self.value))
        return self._usage

    # defines a random average of capacity - API should probably be able to
    # determine average of capacity based on capacity value and obejct_id
    @property
    def average(self):
        if not hasattr(self, '_average'):
            self._average = randint(0, int(self.value))
        return self._average


class Node(StringIdAPIResourceWrapper):
    """Wrapper for the Node object  returned by the
    dummy model.
    """
    _attrs = ['id', 'pm_address', 'cpus', 'memory_mb', 'service_host',
        'local_gb', 'pm_user']

    @classmethod
    def manager(cls):
        nc = nova.nova_client.Client(
                NOVA_BAREMETAL_CREDS['user'],
                NOVA_BAREMETAL_CREDS['password'],
                NOVA_BAREMETAL_CREDS['tenant'],
                auth_url=NOVA_BAREMETAL_CREDS['auth_url'],
                bypass_url=NOVA_BAREMETAL_CREDS['bypass_url'])
        return nova.baremetal.BareMetalNodeManager(nc)

    @classmethod
    def get(cls, request, node_id):
        node = cls(cls.manager().get(node_id))
        node.request = request

        # FIXME ugly, fix after demo, make abstraction of instance details
        # this is realy not optimal, but i dont hve time do fix it now
        instances, more = nova.server_list(
            request,
            search_opts={'paginate': True},
            all_tenants=True)

        instance_details = {}
        for instance in instances:
            id = (instance.
                  _apiresource._info['OS-EXT-SRV-ATTR:hypervisor_hostname'])
            instance_details[id] = instance

        detail = instance_details.get(node_id)
        if detail:
            addresses = detail._apiresource.addresses.get('ctlplane')
            if addresses:
                node.ip_address_other = (", "
                    .join([addr['addr'] for addr in addresses]))

            node.status = detail._apiresource._info['OS-EXT-STS:vm_state']
            node.power_mamanegemt = ""
            if node.pm_user:
                node.power_mamanegemt = node.pm_user + "/********"
        else:
            node.status = 'unprovisioned'

        return node

    @classmethod
    def list(cls, request):
        return cls.manager().list()

    @classmethod
    def list_unracked(cls, request):
        return [cls(h) for h in dummymodels.Node.objects.all() if (
            h.rack is None)]

    @classmethod
    def create(cls, request, name, mac_address, ip_address, status,
               usage, rack):
        node = dummymodels.Node(name=name, mac_address=mac_address,
                                ip_address=ip_address, status=status,
                                usage=usage, rack=rack)
        node.save()

    @property
    def list_flavors(self):
        if not hasattr(self, '_flavors'):
            # FIXME: just a mock of used instances, add real values
            used_instances = 0

            if not self.rack or not self.rack.resource_class:
                return []
            resource_class = self.rack.resource_class

            added_flavors = tuskarclient(self.request).flavors\
                                                      .list(resource_class.id)
            self._flavors = []
            if added_flavors:
                for f in added_flavors:
                    flavor_obj = Flavor(f)
                    #flavor_obj.max_vms = f.max_vms

                    # FIXME just a mock of used instances, add real values
                    used_instances += 5
                    flavor_obj.used_instances = used_instances
                    self._flavors.append(flavor_obj)

        return self._flavors

    @property
    def capacities(self):
        if not hasattr(self, '_capacities'):
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self._capacities

    @property
    def rack(self):
        try:
            if not hasattr(self, '_rack'):
                # FIXME the node.rack association should be stored somewhere
                self._rack = None
                for rack in Rack.list(self.request):
                    for node_obj in rack.list_nodes:
                        if node_obj.id == self.id:
                            self._rack = rack

            return self._rack
        except:
            msg = "Could not obtain Nodes's rack"
            LOG.debug(exceptions.error_color(msg))
            return None

    @property
    def cpu(self):
        if not hasattr(self, '_cpu'):
            try:
                cpu = dummymodels.Capacity.objects\
                            .filter(node=self._apiresource)\
                            .filter(name='cpu')[0]
            except:
                cpu = dummymodels.Capacity(
                            name='cpu',
                            value=_('Unable to retrieve '
                                    '(Is the node configured properly?)'),
                            unit='')
            self._cpu = Capacity(cpu)
        return self._cpu

    @property
    def ram(self):
        if not hasattr(self, '_ram'):
            try:
                ram = dummymodels.Capacity.objects\
                            .filter(node=self._apiresource)\
                            .filter(name='ram')[0]
            except:
                ram = dummymodels.Capacity(
                            name='ram',
                            value=_('Unable to retrieve '
                                    '(Is the node configured properly?)'),
                            unit='')
            self._ram = Capacity(ram)
        return self._ram

    @property
    def storage(self):
        if not hasattr(self, '_storage'):
            try:
                storage = dummymodels.Capacity.objects\
                                .filter(node=self._apiresource)\
                                .filter(name='storage')[0]
            except:
                storage = dummymodels.Capacity(
                                name='storage',
                                value=_('Unable to retrieve '
                                        '(Is the node configured properly?)'),
                                unit='')
            self._storage = Capacity(storage)
        return self._storage

    @property
    def network(self):
        if not hasattr(self, '_network'):
            try:
                network = dummymodels.Capacity.objects\
                                .filter(node=self._apiresource)\
                                .filter(name='network')[0]
            except:
                network = dummymodels.Capacity(
                                name='network',
                                value=_('Unable to retrieve '
                                        '(Is the node configured properly?)'),
                                unit='')
            self._network = Capacity(network)
        return self._network

    @property
    def vm_capacity(self):
        if not hasattr(self, '_vm_capacity'):
            try:
                value = dummymodels.ResourceClassFlavor.objects\
                            .filter(
                                resource_class__rack__node=self._apiresource)\
                            .aggregate(Max("max_vms"))['max_vms__max']
            except:
                value = _("Unable to retrieve vm capacity")

            vm_capacity = dummymodels.Capacity(name=_("Max VMs"),
                                               value=value,
                                               unit=_("VMs"))
            self._vm_capacity = Capacity(vm_capacity)
        return self._vm_capacity

    @property
    # FIXME: just mock implementation, add proper one
    def running_instances(self):
        return 4

    @property
    # FIXME: just mock implementation, add proper one
    def remaining_capacity(self):
        return 100 - self.running_instances

    @property
    # FIXME: just mock implementation, add proper one
    def is_provisioned(self):
        return self.status != "unprovisioned" and self.rack

    @property
    def alerts(self):
        if not hasattr(self, '_alerts'):
            self._alerts = [Alert(a) for a in
                dummymodels.Alert.objects
                    .filter(object_type='node')
                    .filter(object_id=str(self.id))]
        return self._alerts

    @property
    def mac_address(self):
        try:
            return self._apiresource.interfaces[0]['address']
        except:
            return None


class Rack(StringIdAPIResourceWrapper):
    """Wrapper for the Rack object  returned by the
    dummy model.
    """
    _attrs = ['id', 'name', 'location', 'subnet', 'nodes', 'state']

    @classmethod
    def create(cls, request, name, resource_class_id, location, subnet,
               nodes=[]):
        ## FIXME: set nodes here
        rack = tuskarclient(request).racks.create(
                name=name,
                location=location,
                subnet=subnet,
                nodes=nodes,
                resource_class={'id': resource_class_id},
                slots=0)
        return cls(rack)

    @classmethod
    def update(cls, request, rack_id, kwargs):
        ## FIXME: set nodes here
        correct_kwargs = copy.copy(kwargs)
        # remove rack_id from kwargs (othervise it is duplicated)
        correct_kwargs.pop('rack_id', None)
        # correct data mapping for resource_class
        if 'resource_class_id' in correct_kwargs:
            correct_kwargs['resource_class'] = {
                'id': correct_kwargs.pop('resource_class_id', None)}

        rack = tuskarclient(request).racks.update(rack_id, **correct_kwargs)
        return cls(rack)

    @classmethod
    def list(cls, request, only_free_racks=False):
        if only_free_racks:
            return [Rack(r, request) for r in
                    tuskarclient(request).racks.list() if (
                        r.resource_class is None)]
        else:
            return [Rack(r, request) for r in
                    tuskarclient(request).racks.list()]

    @classmethod
    def get(cls, request, rack_id):
        rack = cls(tuskarclient(request).racks.get(rack_id))
        rack.request = request
        return rack

    @property
    def resource_class_id(self):
        rclass = getattr(self._apiresource, 'resource_class', None)
        return rclass['id'] if rclass else None

    @classmethod
    def delete(cls, request, rack_id):
        tuskarclient(request).racks.delete(rack_id)

    @property
    def node_ids(self):
        """ List of unicode ids of nodes added to rack"""
        return [
            unicode(node['id']) for node in (
                self._apiresource.nodes)]

    ## FIXME: this will have to be rewritten to ultimately
    ## fetch nodes from nova baremetal
    @property
    def list_nodes(self):
        if not hasattr(self, '_nodes'):
            self._nodes = [Node.get(self.request, node['id']) for node in (
                self._apiresource.nodes)]
        return self._nodes

    def nodes_count(self):
        return len(self._apiresource.nodes)

    # The idea here is to take a list of MAC addresses and assign them to
    # our rack. I'm attaching this here so that we can take one list, versus
    # potentially making a long series of API calls.
    # The present implementation makes no attempt at optimization since this
    # is likely short-lived until a real API is implemented.
    @classmethod
    def register_nodes(cls, rack_id, nodes_list):
        for mac in nodes_list:
            # search for MAC
            try:
                node = dummymodels.Node.objects.get(mac_address=mac)
                if node is not None:
                    node.rack_id = rack_id
                    node.save()
            except:
                # FIXME: It is unclear what we're supposed to do in this case.
                # I create a new Node, but it's possible we should not
                # allow new entries here.
                # FIXME: If this stays, we should probably add Capabilities
                # here so that graphs work as expected.
                Node.create(None, mac, mac, None, None, None, rack_id)

    @property
    def resource_class(self):
        if not hasattr(self, '_resource_class'):
            rclass = getattr(self._apiresource, 'resource_class', None)
            if rclass:
                self._resource_class = ResourceClass.get(self.request,
                                                         rclass['id'])
            else:
                self._resource_class = None
        return self._resource_class

    @property
    def capacities(self):
        if not hasattr(self, '_capacities'):
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities]
        return self._capacities

    @property
    def vm_capacity(self):
        """ Rack VM Capacity is maximum value from It's Resource Class's
            Flavors max_vms (considering flavor sizes are multiples).
        """
        if not hasattr(self, '_vm_capacity'):
            try:
                value = max([flavor.max_vms for flavor in
                             self.resource_class.list_flavors])
            except:
                value = None
            self._vm_capacity = Capacity({'name': "VM Capacity",
                                          'value': value,
                                          'unit': 'VMs'})
        return self._vm_capacity

    @property
    def alerts(self):
        if not hasattr(self, '_alerts'):
            self._alerts = [Alert(a) for a in
                dummymodels.Alert.objects
                    .filter(object_type='rack')
                    .filter(object_id=int(self.id))]
        return self._alerts

    @property
    def aggregated_alerts(self):
        # FIXME: for now return only list of nodes (particular alerts are not
        # used)
        return [node for node in self.list_nodes if node.alerts]

    @property
    def list_flavors(self):

        if not hasattr(self, '_flavors'):
            # FIXME just a mock of used instances, add real values
            used_instances = 0

            if not self.resource_class:
                return []
            added_flavors = tuskarclient(self.request).flavors\
                                .list(self.resource_class.id)
            self._flavors = []
            if added_flavors:
                for f in added_flavors:
                    flavor_obj = Flavor(f)
                    #flavor_obj.max_vms = f.max_vms

                    # FIXME just a mock of used instances, add real values
                    used_instances += 2
                    flavor_obj.used_instances = used_instances
                    self._flavors.append(flavor_obj)

        return self._flavors

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
    def provision(cls, request, rack_id):
        tuskarclient(request).data_centers.provision_all()


class ResourceClass(StringIdAPIResourceWrapper):
    """Wrapper for the ResourceClass object  returned by the
    dummy model.
    """
    _attrs = ['id', 'name', 'service_type', 'racks']

    @classmethod
    def get(cls, request, resource_class_id):
        rc = cls(tuskarclient(request).resource_classes.get(resource_class_id))
        return rc

    @classmethod
    def create(self, request, name, service_type, flavors):
        return ResourceClass(
            tuskarclient(request).resource_classes.create(
                name=name,
                service_type=service_type,
                flavors=flavors))

    @classmethod
    def list(cls, request):
        return [cls(rc) for rc in (
            tuskarclient(request).resource_classes.list())]

    @classmethod
    def update(cls, request, resource_class_id, **kwargs):
        resource_class = cls(tuskarclient(request).resource_classes.update(
                resource_class_id, **kwargs))

        ## FIXME: flavors have to be updated separately, seems less than ideal
        for flavor_id in resource_class.flavors_ids:
            Flavor.delete(request, resource_class.id, flavor_id)
        for flavor in kwargs['flavors']:
            Flavor.create(request, resource_class.id, **flavor)

        return resource_class

    @property
    def deletable(self):
        return (len(self.list_racks) <= 0)

    @classmethod
    def delete(cls, request, resource_class_id):
        tuskarclient(request).resource_classes.delete(resource_class_id)

    @property
    def racks_ids(self):
        """ List of unicode ids of racks added to resource class """
        return [
            unicode(rack['id']) for rack in (
                self._apiresource.racks)]

    @property
    def list_racks(self):
        """ List of racks added to ResourceClass """
        if not hasattr(self, '_racks'):
            self._racks = [Rack.get(self.request, rid) for rid in (
                self.racks_ids)]
        return self._racks

    @property
    def capacities(self):
        """Aggregates Rack capacities values
        """
        if not hasattr(self, '_capacities'):
            capacities = [rack.capacities for rack in self.list_racks]

            def add_capacities(c1, c2):
                return [Capacity({'name': a.name,
                                 'value': int(a.value) + int(b.value),
                                 'unit': a.unit}) for a, b in zip(c1, c2)]

            self._capacities = reduce(add_capacities, capacities)
        return self._capacities

    @property
    def all_racks(self):
        """ List of racks added to ResourceClass + list of free racks,
        meaning racks that don't belong to any ResourceClass"""
        if not hasattr(self, '_all_racks'):
            self._all_racks =\
                [r for r in (
                    Rack.list(self.request)) if (
                        r.resource_class_id is None or
                        str(r.resource_class_id) == self.id)]
        return self._all_racks

    @property
    def flavors_ids(self):
        """ List of unicode ids of flavors added to resource class """
        return [unicode(flavor.id) for flavor in self.list_flavors]

    # FIXME: for now, we display list of flavor templates when
    # editing a resource class - we have to set id of flavor template, not
    # flavor
    @property
    def flavortemplates_ids(self):
        """ List of unicode ids of flavor templates added to resource class """
        return [unicode(ft.flavor_template.id) for ft in self.list_flavors]

    @property
    def list_flavors(self):
        if not hasattr(self, '_flavors'):
            # FIXME just a mock of used instances, add real values
            used_instances = 0

            added_flavors = tuskarclient(self.request).flavors.list(self.id)
            self._flavors = []
            for f in added_flavors:
                flavor_obj = Flavor(f)
                #flavor_obj.max_vms = f.max_vms

                # FIXME just a mock of used instances, add real values
                used_instances += 5
                flavor_obj.used_instances = used_instances
                self._flavors.append(flavor_obj)

        return self._flavors

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
    def all_flavors(self):
        """ Joined relation table resourceclassflavor with all global flavors
        """
        if not hasattr(self, '_all_flavors'):
            my_flavors = self.list_flavors
            self._all_flavors = []
            for flavor in FlavorTemplate.list(self.request):
                fname = "%s.%s" % (self.name, flavor.name)
                f = next((f for f in my_flavors if f.name == fname), None)
                if f:
                    flavor.max_vms = f.max_vms
                self._all_flavors.append(flavor)
        return self._all_flavors

    @property
    def nodes(self):
        if not hasattr(self, '_nodes'):
            nodes_array = [rack.nodes for rack in self.racks]
            self._nodes = [node for nodes in nodes_array for node in nodes]
        return self._nodes

    @property
    def nodes_count(self):
        return len(self.nodes)

    @property
    def racks_count(self):
        return len(self.racks)

    @property
    def vm_capacity(self):
        """ Resource Class VM Capacity is maximum value from It's Flavors
            max_vms (considering flavor sizes are multiples), multipled by
            number of Racks in Resource Class.
        """
        if not hasattr(self, '_vm_capacity'):
            try:
                value = self.racks_count * max([flavor.max_vms for flavor in
                                                self.list_flavors])
            except:
                value = _("Unable to retrieve vm capacity")
            self._vm_capacity = Capacity({'name': _("VM Capacity"),
                                          'value': value,
                                          'unit': _('VMs')})
        return self._vm_capacity

    def set_racks(self, request, racks_ids):
        # FIXME: there is a bug now in tuskar, we have to remove all racks at
        # first and then add new ones:
        # https://github.com/tuskar/tuskar/issues/37
        tuskarclient(request).resource_classes.update(self.id, racks=[])
        racks = [{'id': rid} for rid in racks_ids]
        tuskarclient(request).resource_classes.update(self.id, racks=racks)

    @property
    def aggregated_alerts(self):
        # FIXME: for now return only list of racks (particular alerts are not
        # used)
        return [rack for rack in self.list_racks if (rack.alerts +
            rack.aggregated_alerts)]

    @property
    def has_provisioned_rack(self):
        return any([rack.is_provisioned for rack in self.list_racks])


class FlavorTemplate(StringIdAPIResourceWrapper):
    """Wrapper for the Flavor object returned by the
    dummy model.
    """
    _attrs = ['name']

    @property
    def max_vms(self):
        return getattr(self, '_max_vms', '0')

    @max_vms.setter
    def max_vms(self, value='0'):
        self._max_vms = value

    @property
    def used_instances(self):
        return getattr(self, '_used_instances', 0)

    @used_instances.setter
    def used_instances(self, value=0):
        self._used_instances = value

    @classmethod
    def list(cls, request, only_free_racks=False):
        return [cls(f) for f in dummymodels.FlavorTemplate.objects.all()]

    @classmethod
    def get(cls, request, flavor_id):
        return cls(dummymodels.FlavorTemplate.objects.get(id=flavor_id))

    @classmethod
    def create(cls, request,
               name, cpu, memory, storage, ephemeral_disk, swap_disk):
        template = dummymodels.FlavorTemplate(name=name)
        template.save()
        Capacity.create(request, template, 'cpu', cpu, '')
        Capacity.create(request, template, 'memory', memory, 'MB')
        Capacity.create(request, template, 'storage', storage, 'GB')
        Capacity.create(request,
                        template, 'ephemeral_disk', ephemeral_disk, 'GB')
        Capacity.create(request, template, 'swap_disk', swap_disk, 'MB')

    @property
    def capacities(self):
        if not hasattr(self, '_capacities'):
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self._capacities

    def capacity(self, capacity_name):
        key = "_%s" % capacity_name
        if not hasattr(self, key):
            try:
                capacity = [c for c in self.capacities if (
                    c.name == capacity_name)][0]
            except:
                capacity = dummymodels.Capacity(
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
        return randint(0, int(self.cpu.value))

    # defines a random average of capacity - API should probably be able to
    # determine average of capacity based on capacity value and obejct_id
    def vms_over_time(self, start_time, end_time):
        values = []
        current_time = start_time
        while current_time <= end_time:
            values.append(
                {'date': current_time,
                 'active_vms': randint(0, self.running_virtual_machines)})
            current_time += timedelta(hours=1)

        return values

    @classmethod
    def update(cls, request, template_id, name, cpu, memory, storage,
               ephemeral_disk, swap_disk):
        t = dummymodels.FlavorTemplate.objects.get(id=template_id)
        t.name = name
        t.save()
        template = cls(t)
        Capacity.update(request, template.cpu.id, template._apiresource,
                        'cpu', cpu, '')
        Capacity.update(request, template.memory.id, template._apiresource,
                        'memory', memory, 'MB')
        Capacity.update(request, template.storage.id, template._apiresource,
                        'storage', storage, 'GB')
        Capacity.update(request, template.ephemeral_disk.id,
                        template._apiresource, 'ephemeral_disk',
                        ephemeral_disk, 'GB')
        Capacity.update(request, template.swap_disk.id, template._apiresource,
                        'swap_disk', swap_disk, 'MB')
        return template

    @classmethod
    def delete(cls, request, template_id):
        dummymodels.FlavorTemplate.objects.get(id=template_id).delete()


class Flavor(StringIdAPIResourceWrapper):
    """Wrapper for the Flavor object returned by Tuskar.
    """
    _attrs = ['name', 'max_vms']

    @classmethod
    def create(cls, request, resource_class_id, name, max_vms, capacities):
        return cls(tuskarclient(request).flavors.create(
                resource_class_id,
                name=name,
                max_vms=max_vms,
                capacities=capacities))

    @classmethod
    def delete(cls, request, resource_class_id, flavor_id):
        tuskarclient(request).flavors.delete(resource_class_id, flavor_id)

    # FIXME: returns flavor template for this flavor
    @property
    def flavor_template(self):
        # strip resource class prefix from flavor name before comparing:
        fname = re.sub(r'^.*\.', '', self.name)
        return next(f for f in FlavorTemplate.list(None) if (
            f.name == fname))

    @property
    def capacities(self):
        if not hasattr(self, '_capacities'):
            ## FIXME: should we distinguish between tuskar
            ## capacities and our internal capacities?
            CapacityStruct = namedtuple('CapacityStruct', 'name value unit')
            self._capacities = [Capacity(CapacityStruct(
                        name=c['name'],
                        value=c['value'],
                        unit=c['unit'])) for c in self._apiresource.capacities]
        return self._capacities

    def capacity(self, capacity_name):
        key = "_%s" % capacity_name
        if not hasattr(self, key):
            try:
                capacity = [c for c in self.capacities if (
                    c.name == capacity_name)][0]
            except:
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
        return randint(0, int(self.cpu.value))

    # defines a random average of capacity - API should probably be able to
    # determine average of capacity based on capacity value and obejct_id
    def vms_over_time(self, start_time, end_time):
        values = []
        current_time = start_time
        while current_time <= end_time:
            values.append({'date': current_time,
                           'value': randint(0, self.running_virtual_machines)})
            current_time += timedelta(hours=1)

        return values
