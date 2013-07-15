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
from datetime import timedelta
from random import randint

from django.conf import settings
from django.db.models import Sum, Max
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions

from tuskarclient.v1 import client as tuskar_client

from openstack_dashboard.api import base
import openstack_dashboard.dashboards.infrastructure.models as dummymodels


LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(settings, 'TUSKAR_ENDPOINT_URL')


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
    _attrs = ['name', 'mac_address', 'ip_address', 'status', 'usage', 'rack']

    @classmethod
    def get(cls, request, node_id):
        return cls(dummymodels.Node.objects.get(id=node_id))

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
    def capacities(self):
        if not hasattr(self, '_capacities'):
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self._capacities

    @property
    def rack(self):
        if not hasattr(self, '_rack'):
            self._rack = self._apiresource.rack
        return self._rack

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
    def is_provisioned(self):
        return False

    @property
    def alerts(self):
        if not hasattr(self, '_alerts'):
            self._alerts = [Alert(a) for a in
                dummymodels.Alert.objects
                    .filter(object_type='node')
                    .filter(object_id=int(self.id))]
        return self._alerts


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
            return [Rack(r) for r in
                    tuskarclient(request).racks.list() if (
                        r.resource_class is None)]
        else:
            return [Rack(r) for r in
                    tuskarclient(request).racks.list()]

    @classmethod
    def get(cls, request, rack_id):
        rack = cls(tuskarclient(request).racks.get(rack_id))
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
        return []
        #if not hasattr(self, '_nodes'):
        #    self._nodes = [Node(h) for h in self._apiresource.node_set.all()]
        #return self._nodes

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
        if not hasattr(self, '_vm_capacity'):
            try:
                value = dummymodels.ResourceClassFlavor.objects\
                            .filter(resource_class__rack=self._apiresource)\
                            .aggregate(Max("max_vms"))['max_vms__max']
            except:
                value = _("Unable to retrieve vm capacity")

            vm_capacity = dummymodels.Capacity(name=_("Max VMs"),
                                               value=value,
                                               unit=_("VMs"))
            self._vm_capacity = Capacity(vm_capacity)
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
    def running_virtual_machines(self):
        if not hasattr(self, '_running_virtual_machines'):
            self._running_virtual_machines =\
                                    copy.deepcopy(self.list_flavors)
            for vm in self._running_virtual_machines:
                vm.max_vms /= (vm.max_vms % 7) + 1
        return self._running_virtual_machines

    @property
    def cpu(self):
        if not hasattr(self, '_cpu'):
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack__resource_class=self._apiresource)\
                        .values('name', 'unit').annotate(value=Sum('value'))\
                        .filter(name='cpu')[0]
            except:
                attrs = {'name': 'cpu',
                         'value': _('Unable to retrieve '
                                    '(Are the nodes configured properly?)'),
                         'unit': ''}
            cpu = dummymodels.Capacity(name=attrs['name'],
                                             value=attrs['value'],
                                             unit=attrs['unit'])
            self._cpu = Capacity(cpu)
        return self._cpu

    @property
    def ram(self):
        if not hasattr(self, '_ram'):
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack__resource_class=self._apiresource)\
                        .values('name', 'unit').annotate(value=Sum('value'))\
                        .filter(name='ram')[0]
            except:
                attrs = {'name': 'ram',
                         'value': _('Unable to retrieve '
                                    '(Are the nodes configured properly?)'),
                         'unit': ''}
            ram = dummymodels.Capacity(name=attrs['name'],
                                             value=attrs['value'],
                                             unit=attrs['unit'])
            self._ram = Capacity(ram)
        return self._ram

    @property
    def storage(self):
        if not hasattr(self, '_storage'):
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack__resource_class=self._apiresource)\
                        .values('name', 'unit').annotate(value=Sum('value'))\
                        .filter(name='storage')[0]
            except:
                attrs = {'name': 'storage',
                         'value': _('Unable to retrieve '
                                    '(Are the nodes configured properly?)'),
                         'unit': ''}
            storage = dummymodels.Capacity(name=attrs['name'],
                                                 value=attrs['value'],
                                                 unit=attrs['unit'])
            self._storage = Capacity(storage)
        return self._storage

    @property
    def network(self):
        if not hasattr(self, '_network'):
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack__resource_class=self._apiresource)\
                        .values('name', 'unit').annotate(value=Sum('value'))\
                        .filter(name='network')[0]
            except:
                attrs = {'name': 'network',
                         'value': _('Unable to retrieve '
                                    '(Are the nodes configured properly?)'),
                         'unit': ''}
            network = dummymodels.Capacity(name=attrs['name'],
                                           value=attrs['value'],
                                           unit=attrs['unit'])
            self._network = Capacity(network)
        return self._network

    @property
    def vm_capacity(self):
        if not hasattr(self, '_vm_capacity'):
            try:
                value = dummymodels.ResourceClassFlavor.objects\
                            .filter(resource_class=self._apiresource)\
                            .aggregate(Max("max_vms"))['max_vms__max']
            except:
                value = _("Unable to retrieve vm capacity")

            vm_capacity = dummymodels.Capacity(name=_("Max VMs"),
                                               value=value,
                                               unit=_("VMs"))
            self._vm_capacity = Capacity(vm_capacity)
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
        # arbitrary number
        return len(self.resource_classes) * 2

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
                        'ram', ram, 'MB')
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
        # arbitrary number
        return len(self.resource_classes) * 2

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
