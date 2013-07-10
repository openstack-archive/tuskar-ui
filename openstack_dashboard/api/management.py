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
from datetime import timedelta
from random import randint

from django.db.models import Sum, Max
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.api import base
import openstack_dashboard.dashboards.infrastructure.models as dummymodels


LOG = logging.getLogger(__name__)


class StringIdAPIResourceWrapper(base.APIResourceWrapper):
    # horizon DataTable class expects ids to be string,
    # if it's not string, then comparison in
    # horizon/tables/base.py:get_object_by_id fails.
    # Because of this, ids returned from dummy api are converted to string
    # (luckily django autoconverts strings to integers when passing string to
    # django model id)
    @property
    def id(self):
        return str(self._apiresource.id)

    def set_request(self, request):
        self.request = request


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
        if "_usage" not in self.__dict__:
            self._usage = randint(0, self.value)
        return self.__dict__['_usage']

    # defines a random average of capacity - API should probably be able to
    # determine average of capacity based on capacity value and obejct_id
    @property
    def average(self):
        if "_average" not in self.__dict__:
            self._average = randint(0, self.value)
        return self.__dict__['_average']


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
        if "_capacities" not in self.__dict__:
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self.__dict__['_capacities']

    @property
    def rack(self):
        if "_rack" not in self.__dict__:
            self._rack = self._apiresource.rack
        return self.__dict__['_rack']

    @property
    def cpu(self):
        if "_cpu" not in self.__dict__:
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
        return self.__dict__['_cpu']

    @property
    def ram(self):
        if "_ram" not in self.__dict__:
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
        return self.__dict__['_ram']

    @property
    def storage(self):
        if "_storage" not in self.__dict__:
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
        return self.__dict__['_storage']

    @property
    def network(self):
        if "_network" not in self.__dict__:
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
        return self.__dict__['_network']

    @property
    def vm_capacity(self):
        if "_vm_capacity" not in self.__dict__:
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
        return self.__dict__['_vm_capacity']


class Rack(StringIdAPIResourceWrapper):
    """Wrapper for the Rack object  returned by the
    dummy model.
    """
    _attrs = ['name', 'resource_class_id', 'location', 'subnet']

    @classmethod
    def create(cls, request, name, resource_class_id, location, subnet):
        rack = dummymodels.Rack(name=name,
                                resource_class_id=resource_class_id,
                                location=location, subnet=subnet)
        rack.save()
        return rack

    @classmethod
    def list(cls, request, only_free_racks=False):
        if only_free_racks:
            return [cls(r) for r in dummymodels.Rack.objects.all() if (
                r.resource_class is None)]
        else:
            return [cls(r) for r in dummymodels.Rack.objects.all()]

    @classmethod
    def get(cls, request, rack_id):
        return cls(dummymodels.Rack.objects.get(id=rack_id))

    @property
    def capacities(self):
        if "_capacities" not in self.__dict__:
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self.__dict__['_capacities']

    @property
    def cpu(self):
        if "_cpu" not in self.__dict__:
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack=self._apiresource)\
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
        return self.__dict__['_cpu']

    @property
    def ram(self):
        if "_ram" not in self.__dict__:
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack=self._apiresource)\
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
        return self.__dict__['_ram']

    @property
    def storage(self):
        if "_storage" not in self.__dict__:
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack=self._apiresource)\
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
        return self.__dict__['_storage']

    @property
    def network(self):
        if "_network" not in self.__dict__:
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(node__rack=self._apiresource)\
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
        return self.__dict__['_network']

    @property
    def vm_capacity(self):
        if "_vm_capacity" not in self.__dict__:
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
        return self.__dict__['_vm_capacity']

    @classmethod
    def delete(cls, request, rack_id):
        dummymodels.Rack.objects.get(id=rack_id).delete()

    @property
    def nodes(self):
        if "_nodes" not in self.__dict__:
            self._nodes = [Node(h) for h in self._apiresource.node_set.all()]
        return self.__dict__['_nodes']

    def nodes_count(self):
        return len(self.nodes)

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
        if "_resource_class" not in self.__dict__:
            self._resource_class = self._apiresource.resource_class
        return self.__dict__['_resource_class']

    @classmethod
    def update(cls, rack_id, kwargs):
        rack = dummymodels.Rack.objects.get(id=rack_id)
        rack.name = kwargs['name']
        rack.location = kwargs['location']
        rack.subnet = kwargs['subnet']
        rack.resource_class_id = kwargs['resource_class_id']
        rack.save()
        return cls(rack)


##########################################################################
# ResourceClass
##########################################################################
class ResourceClass(StringIdAPIResourceWrapper):
    """Wrapper for the ResourceClass object  returned by the
    dummy model.
    """
    _attrs = ['name', 'service_type', 'status']

    ##########################################################################
    # ResourceClass Class methods
    ##########################################################################
    @classmethod
    def get(cls, request, resource_class_id):
        obj = cls(dummymodels.ResourceClass.objects.get(
            id=resource_class_id))
        obj.set_request(request)
        return obj

    @classmethod
    def create(self, request, name, service_type):
        rc = dummymodels.ResourceClass(
            name=name,
            service_type=service_type)

        rc.save()
        return ResourceClass(rc)

    @classmethod
    def list(self, request):
        return [
            ResourceClass(rc) for rc in (
                dummymodels.ResourceClass.objects.all())]

    @classmethod
    def update(cls, request, resource_class_id, **kwargs):
        rc = dummymodels.ResourceClass.objects.get(id=resource_class_id)
        rc.name = kwargs['name']
        rc.service_type = kwargs['service_type']
        rc.save()
        return cls(rc)

    @classmethod
    def delete(cls, request, resource_class_id):
        dummymodels.ResourceClass.objects.get(id=resource_class_id).delete()

    ##########################################################################
    # ResourceClass Properties
    ##########################################################################
    @property
    def racks_ids(self):
        """ List of unicode ids of racks added to resource class """
        return [
            unicode(rack.id) for rack in (
                self.racks)]

    @property
    def racks(self):
        """ List of racks added to ResourceClass """
        if "_racks" not in self.__dict__:
            self._racks =\
                [Rack(r) for r in (
                    self._apiresource.rack_set.all())]
        return self.__dict__['_racks']

    @property
    def all_racks(self):
        """ List of racks added to ResourceClass + list of free racks,
        meaning racks that don't belong to any ResourceClass"""
        if "_all_racks" not in self.__dict__:
            self._all_racks =\
                [r for r in (
                    Rack.list(self.request)) if (
                        r.resource_class_id is None or
                        r._apiresource.resource_class == self._apiresource)]
        return self.__dict__['_all_racks']

    @property
    def resource_class_flavors(self):
        """ Relation table resourceclassflavor """
        if "_resource_class_flavors" not in self.__dict__:
            self._resource_class_flavors = [ResourceClassFlavor(r) for r in (
                self._apiresource.resourceclassflavor_set.all())]
        return self.__dict__['_resource_class_flavors']

    @property
    def flavors_ids(self):
        """ List of unicode ids of flavors added to resource class """
        return [
            unicode(flavor.flavor.id) for flavor in (
                self.resource_class_flavors)]

    @property
    def flavors(self):
        """ Joined relation table resourceclassflavor and flavor together """
        if "_flavors" not in self.__dict__:
            added_flavors = self.resource_class_flavors
            self._flavors = []
            for f in added_flavors:
                flavor_obj = Flavor.get(self.request, f.flavor.id)
                flavor_obj.set_max_vms(f.max_vms)
                self._flavors.append(flavor_obj)

        return self.__dict__['_flavors']

    @property
    def all_flavors(self):
        """ Joined relation table resourceclassflavor with all global flavors
        """
        if "_all_flavors" not in self.__dict__:
            all_flavors = Flavor.list(self.request)

            added_resourceclassflavors = \
                self._apiresource.resourceclassflavor_set.all()
            added_flavors = {}
            for added_flavor in added_resourceclassflavors:
                added_flavors[str(added_flavor.flavor_id)] = added_flavor

            self._all_flavors = []
            for f in all_flavors:
                added_flavor = added_flavors.get(f.id)
                if added_flavor:
                    f.set_max_vms(added_flavor.max_vms)
                self._all_flavors.append(f)

        return self.__dict__['_all_flavors']

    @property
    def nodes(self):
        if "_nodes" not in self.__dict__:
            nodes_array = [rack.nodes for rack in self.racks]
            self._nodes = [node for nodes in nodes_array for node in nodes]
        return self.__dict__['_nodes']

    @property
    def nodes_count(self):
        return len(self.nodes)

    @property
    def racks_count(self):
        return len(self.racks)

    @property
    def running_virtual_machines(self):
        if "_running_virtual_machines" not in self.__dict__:
            self._running_virtual_machines =\
                                    copy.deepcopy(self.resource_class_flavors)
            for vm in self._running_virtual_machines:
                vm.max_vms /= (vm.max_vms % 7) + 1
        return self.__dict__['_running_virtual_machines']

    @property
    def cpu(self):
        if "_cpu" not in self.__dict__:
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
        return self.__dict__['_cpu']

    @property
    def ram(self):
        if "_ram" not in self.__dict__:
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
        return self.__dict__['_ram']

    @property
    def storage(self):
        if "_storage" not in self.__dict__:
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
        return self.__dict__['_storage']

    @property
    def network(self):
        if "_network" not in self.__dict__:
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
        return self.__dict__['_network']

    @property
    def vm_capacity(self):
        if "_vm_capacity" not in self.__dict__:
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
        return self.__dict__['_vm_capacity']

    ##########################################################################
    # ResourceClass Instance methods
    ##########################################################################
    def set_flavors(self, request, flavors_ids, max_vms=None):
        # simply delete all and create new flavors, that'is
        # how the horizon flavors work
        max_vms = max_vms or {}

        for flavor_id in self.flavors_ids:
            ResourceClassFlavor.delete(request,
                                       self.id,
                                       flavor_id)

        for flavor_id in flavors_ids:
            flavor = Flavor.get(request, flavor_id)
            ResourceClassFlavor.create(
                request,
                max_vms=max_vms.get(flavor.id),
                flavor=flavor._apiresource,
                resource_class=self._apiresource)

    def set_racks(self, request, racks_ids):
        # simply delete all and create new racks
        for rack_id in self.racks_ids:
            rack = Rack.get(request, rack_id)
            rack._apiresource.resource_class = None
            rack._apiresource.save()

        for rack_id in racks_ids:
            rack = Rack.get(request, rack_id)
            rack._apiresource.resource_class = self._apiresource
            rack._apiresource.save()


class Flavor(StringIdAPIResourceWrapper):
    """Wrapper for the Flavor object returned by the
    dummy model.
    """
    _attrs = ['name']

    @property
    def max_vms(self):
        return getattr(self, '_max_vms', '0')

    def set_max_vms(self, value='0'):
        self._max_vms = value

    @classmethod
    def list(cls, request, only_free_racks=False):
        return [cls(f) for f in dummymodels.Flavor.objects.all()]

    @classmethod
    def get(cls, request, flavor_id):
        return cls(dummymodels.Flavor.objects.get(id=flavor_id))

    @classmethod
    def create(cls, request,
               name, vcpu, ram, root_disk, ephemeral_disk, swap_disk):
        flavor = dummymodels.Flavor(name=name)
        flavor.save()
        Capacity.create(request, flavor, 'vcpu', vcpu, '')
        Capacity.create(request, flavor, 'ram', ram, 'MB')
        Capacity.create(request, flavor, 'root_disk', root_disk, 'GB')
        Capacity.create(request,
                        flavor, 'ephemeral_disk', ephemeral_disk, 'GB')
        Capacity.create(request, flavor, 'swap_disk', swap_disk, 'MB')

    @property
    def capacities(self):
        if "_capacities" not in self.__dict__:
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self.__dict__['_capacities']

    def capacity(self, capacity_name):
        key = "_%s" % capacity_name
        if key not in self.__dict__:
            try:
                capacity = [c for c in self.capacities if (
                    c.name == capacity_name)][0]
            except:
                capacity = dummymodels.Capacity(
                    name=capacity_name,
                    value=_('Unable to retrieve '
                            '(Is the flavor configured properly?)'),
                    unit='')
            self.__dict__[key] = capacity
        return self.__dict__[key]

    @property
    def vcpu(self):
        return self.capacity('vcpu')

    @property
    def ram(self):
        return self.capacity('ram')

    @property
    def root_disk(self):
        return self.capacity('root_disk')

    @property
    def ephemeral_disk(self):
        return self.capacity('ephemeral_disk')

    @property
    def swap_disk(self):
        return self.capacity('swap_disk')

    @property
    def resource_class_flavors(self):
        if "_resource_class_flavors" not in self.__dict__:
            self._resource_class_flavors = [ResourceClassFlavor(r) for r in (
                self._apiresource.resourceclassflavor_set.all())]
        return self.__dict__['_resource_class_flavors']

    @property
    def resource_classes(self):
        if "_resource_classes" not in self.__dict__:
            added_flavors = self.resource_class_flavors
            self._resource_classes = []
            for f in added_flavors:
                self._resource_classes.append(ResourceClass(f.resource_class))

        return self.__dict__['_resource_classes']

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

    @classmethod
    def update(cls, request, flavor_id, name, vcpu, ram, root_disk,
               ephemeral_disk, swap_disk):
        f = dummymodels.Flavor.objects.get(id=flavor_id)
        f.name = name
        f.save()
        flavor = cls(f)
        Capacity.update(request, flavor.vcpu.id, flavor._apiresource,
                        'vcpu', vcpu, '')
        Capacity.update(request, flavor.ram.id, flavor._apiresource,
                        'ram', ram, 'MB')
        Capacity.update(request, flavor.root_disk.id, flavor._apiresource,
                        'root_disk', root_disk, 'GB')
        Capacity.update(request, flavor.ephemeral_disk.id, flavor._apiresource,
                        'ephemeral_disk', ephemeral_disk, 'GB')
        Capacity.update(request, flavor.swap_disk.id, flavor._apiresource,
                        'swap_disk', swap_disk, 'MB')
        return flavor

    @classmethod
    def delete(cls, request, flavor_id):
        dummymodels.Flavor.objects.get(id=flavor_id).delete()


class ResourceClassFlavor(StringIdAPIResourceWrapper):
    """ FIXME this class will probably go away when connected to real API,
    real API doesn't have this realtion Table as separate entity"""

    """Wrapper for the ResourceClassFlavor object  returned by the
    dummy model.
    """

    _attrs = ['max_vms', 'flavor', 'resource_class']

    @property
    def flavor(self):
        if '_flavor' not in self.__dict__:
            self._flavor = self._apiresource.flavor
        return self.__dict__['_flavor']

    @property
    def resource_class(self):
        if '_resource_class' not in self.__dict__:
            self._resource_class = self._apiresource.resource_class
        return self.__dict__['_resource_class']

    @classmethod
    def create(cls, request, resource_class, flavor, max_vms=0):
        rc = dummymodels.ResourceClassFlavor(
            max_vms=max_vms,
            resource_class=resource_class,
            flavor=flavor)
        rc.save()
        return ResourceClassFlavor(rc)

    @classmethod
    def delete(cls, request, resource_class_id, flavor_id):
        dummymodels.ResourceClassFlavor.objects.filter(
            resource_class_id=resource_class_id,
            flavor_id=flavor_id).delete()
