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

from django.db.models import Sum
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


class Host(StringIdAPIResourceWrapper):
    """Wrapper for the Host object  returned by the
    dummy model.
    """
    _attrs = ['name', 'mac_address', 'ip_address', 'status', 'usage']

    @classmethod
    def get(cls, request, host_id):
        return cls(dummymodels.Host.objects.get(id=host_id))

    @property
    def capacities(self):
        if "_capacities" not in self.__dict__:
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self.__dict__['_capacities']


class Rack(StringIdAPIResourceWrapper):
    """Wrapper for the Rack object  returned by the
    dummy model.
    """
    _attrs = ['name', 'resource_class_id']

    @classmethod
    def create(cls, request, name, resource_class_id):
        rack = dummymodels.Rack(name=name,
                                resource_class_id=resource_class_id)
        rack.save()

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

    @classmethod
    def delete(cls, request, rack_id):
        dummymodels.Rack.objects.get(id=rack_id).delete()

    @property
    def hosts(self):
        if "_hosts" not in self.__dict__:
            self._hosts = [Host(h) for h in self._apiresource.host_set.all()]
        return self.__dict__['_hosts']

    def hosts_count(self):
        return len(self.hosts)


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
    def delete(cls, request, flavor_id):
        dummymodels.Flavor.objects.get(id=flavor_id).delete()

    """FIXME: instance methods, shoud they stay?"""
    ##########################################################################
    # ResourceClass Properties
    ##########################################################################
    @property
    def resources_ids(self):
        """ List of unicode ids of resources added to resource class """
        return [
            unicode(resource.id) for resource in (
                self.resources)]

    @property
    def resources(self):
        """ List of resources added to ResourceClass """
        if "_resources" not in self.__dict__:
            self._resources =\
                [Rack(r) for r in (
                    self._apiresource.rack_set.all())]
        return self.__dict__['_resources']

    @property
    def all_resources(self):
        """ List of resources added to ResourceClass """
        if "_all_resources" not in self.__dict__:
            self._all_resources =\
                [r for r in (
                    Rack.list(self.request)) if (
                        r.resource_class_id is None or
                        r._apiresource.resource_class == self._apiresource)]
        return self.__dict__['_all_resources']

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
                flavor_obj = Flavor(Flavor.get(self.request, f.flavor.id))
                flavor_obj.set_max_vms(f.max_vms)
                self._flavors.append(flavor_obj)

        return self.__dict__['_flavors']

    @property
    def all_flavors(self):
        """ all global flavors with filled data of flavor added to resource
        class """
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
    def hosts(self):
        if "_hosts" not in self.__dict__:
            self._hosts = reduce(lambda x, y: x + y,
                                 [r.hosts for r in self.racks])
        return self.__dict__['_hosts']

    @property
    def hosts_count(self):
        return len(self.hosts)

    @property
    def racks(self):
        if "_racks" not in self.__dict__:
            self._racks = [Rack(r) for r in self._apiresource.rack_set.all()]
        return self.__dict__['_racks']

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
    def total_cpu(self):
        if "_total_cpu" not in self.__dict__:
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(host__rack__resource_class=self._apiresource)\
                        .values('name', 'unit').annotate(value=Sum('value'))\
                        .filter(name='cpu')[0]
            except:
                attrs = {'name': 'cpu',
                         'value': _('Unable to retrieve '
                                    '(Are the hosts configured properly?)'),
                         'unit': ''}
            total_cpu = dummymodels.Capacity(name=attrs['name'],
                                             value=attrs['value'],
                                             unit=attrs['unit'])
            self._total_cpu = Capacity(total_cpu)
        return self.__dict__['_total_cpu']

    @property
    def total_ram(self):
        if "_total_ram" not in self.__dict__:
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(host__rack__resource_class=self._apiresource)\
                        .values('name', 'unit').annotate(value=Sum('value'))\
                        .filter(name='ram')[0]
            except:
                attrs = {'name': 'ram',
                         'value': _('Unable to retrieve '
                                    '(Are the hosts configured properly?)'),
                         'unit': ''}
            total_ram = dummymodels.Capacity(name=attrs['name'],
                                             value=attrs['value'],
                                             unit=attrs['unit'])
            self._total_ram = Capacity(total_ram)
        return self.__dict__['_total_ram']

    @property
    def total_storage(self):
        if "_total_storage" not in self.__dict__:
            try:
                attrs = dummymodels.Capacity.objects\
                        .filter(host__rack__resource_class=self._apiresource)\
                        .values('name', 'unit').annotate(value=Sum('value'))\
                        .filter(name='storage')[0]
            except:
                attrs = {'name': 'storage',
                         'value': _('Unable to retrieve '
                                    '(Are the hosts configured properly?)'),
                         'unit': ''}
            total_storage = dummymodels.Capacity(name=attrs['name'],
                                                 value=attrs['value'],
                                                 unit=attrs['unit'])
            self._total_storage = Capacity(total_storage)
        return self.__dict__['_total_storage']

    ##########################################################################
    # ResourceClass Instance methods
    ##########################################################################
    def get_resource_class_flavor(self, request, flavor_id):
        obj = ResourceClassFlavor(dummymodels.ResourceClassFlavor.objects.get(
            resource_class=self.id,
            flavor=flavor_id))
        return obj

    """FIXME: add this later when using instance methods"""
    """def update_attributes(self, request, **kwargs):
        self._apiresource.name = kwargs['name']
        self._apiresource.service_type = kwargs['service_type']
        self._apiresource.save()
        return True

    def delete(self, request):
        self._apiresource.delete()"""

    #Resource class flavors management
    def set_flavors(self, request, flavors_ids, max_vms):
        # simply delete all and create new flavors, that'is
        # how the horizon flavors work
        added_flavor_ids = self.flavors_ids

        self.remove_flavors(request, added_flavor_ids)
        self.add_flavors(request, flavors_ids, max_vms)

    def remove_flavors(self, request, flavors_ids):
        flavors = []
        for flavor_id in flavors_ids:
            self.get_resource_class_flavor(
                request,
                flavor_id).delete()

    def add_flavors(self, request, flavors_ids, max_vms):
        max_vms = max_vms or {}

        flavors = []
        for flavor_id in flavors_ids:
            flavor = Flavor.get(request, flavor_id)
            ResourceClassFlavor.create(
                request,
                max_vms=max_vms.get(flavor.id),
                flavor=flavor._apiresource,
                resource_class=self._apiresource)

    #ResourceClass resources management
    def set_resources(self, request, resources_ids):
        # simply delete all and create new resources, that'is
        # how the horizon resources work
        added_resource_ids = self.resources_ids

        self.remove_resources(request, added_resource_ids)
        self.add_resources(request, resources_ids)

    def remove_resources(self, request, resources_ids):
        for resource_id in resources_ids:
            resource = Rack.get(request, resource_id)
            resource._apiresource.resource_class = None
            resource._apiresource.save()

    def add_resources(self, request, resources_ids):
        for resource_id in resources_ids:
            resource = Rack.get(request, resource_id)
            resource._apiresource.resource_class = self._apiresource
            resource._apiresource.save()


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
    def create(cls, request, name):
        flavor = dummymodels.Flavor(name=name)
        flavor.save()

    @property
    def capacities(self):
        if "_capacities" not in self.__dict__:
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self.__dict__['_capacities']

    @classmethod
    def update(cls, request, flavor_id, **kwargs):
        flavor = dummymodels.Flavor.objects.get(id=flavor_id)
        flavor.name = kwargs['name']
        flavor.save()
        return cls(flavor)

    @classmethod
    def delete(cls, request, flavor_id):
        dummymodels.Flavor.objects.get(id=flavor_id).delete()


class ResourceClassFlavor(StringIdAPIResourceWrapper):
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

    """FIXME: should not have kwargs"""
    @classmethod
    def create(self, request, **kwargs):
        max_vms = kwargs.get('max_vms') or 0

        rc = dummymodels.ResourceClassFlavor(
            max_vms=max_vms,
            resource_class=kwargs['resource_class'],
            flavor=kwargs['flavor'])
        rc.save()
        return ResourceClass(rc)

    """FIXME: should be class method probably, takes 2 ids, no primary key"""
    def delete(self):
        self._apiresource.delete()
