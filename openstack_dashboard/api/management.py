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


class Capacity(StringIdAPIResourceWrapper):
    """Wrapper for the Capacity object returned by the
    dummy model.
    """
    _attrs = ['name', 'value', 'unit']


class Flavor(StringIdAPIResourceWrapper):
    """Wrapper for the Flavor object returned by the
    dummy model.
    """
    _attrs = ['name']

    @property
    def capacities(self):
        if "_capacities" not in self.__dict__:
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self.__dict__['_capacities']


class Host(StringIdAPIResourceWrapper):
    """Wrapper for the Host object  returned by the
    dummy model.
    """
    _attrs = ['name']

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

    @property
    def hosts(self):
        if "_hosts" not in self.__dict__:
            self._hosts = [Host(h) for h in self._apiresource.host_set.all()]
        return self.__dict__['_hosts']

    @property
    def capacities(self):
        if "_capacities" not in self.__dict__:
            self._capacities = [Capacity(c) for c in
                                self._apiresource.capacities.all()]
        return self.__dict__['_capacities']


class ResourceClass(StringIdAPIResourceWrapper):
    """Wrapper for the ResourceClass object  returned by the
    dummy model.
    """
    _attrs = ['name', 'service_type']

    ##########################################################################
    # ResourceClass Class methods
    ##########################################################################
    @classmethod
    def get(cls, request, resource_class_id):
        return cls(dummymodels.ResourceClass.objects.get(
            id=resource_class_id))

    @classmethod
    def create(self, request, **kwargs):
        rc = dummymodels.ResourceClass(
            name=kwargs['name'],
            service_type=kwargs['service_type'])

        rc.save()
        return ResourceClass(rc)

    @classmethod
    def list(self, request):
        return [
            ResourceClass(rc) for rc in (
                dummymodels.ResourceClass.objects.all())]

    ##########################################################################
    # ResourceClass Properties
    ##########################################################################
    @property
    def resource_class_flavors(self):
        if "_resource_class_flavors" not in self.__dict__:
            self._resource_class_flavors = [ResourceClassFlavor(fc) for fc in
                    self._apiresource.resourceclassflavor_set.all()]
        return self.__dict__['_resource_class_flavors']

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

    ##########################################################################
    # ResourceClass Instance methods
    ##########################################################################
    def update_attributes(self, request, **kwargs):
        self._apiresource.name = kwargs['name']
        self._apiresource.service_type = kwargs['service_type']
        self._apiresource.save()
        return self

    def delete(self, request):
        self._apiresource.delete()


class ResourceClassFlavor(StringIdAPIResourceWrapper):
    """Wrapper for the FlavorCount object  returned by the
    dummy model.
    """
    _attrs = ['max_vms']

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


def flavor_list(request):
    return [Flavor(f) for f in dummymodels.Flavor.objects.all()]


def flavor_get(request, flavor_id):
    return Flavor(dummymodels.Flavor.objects.get(id=flavor_id))


def flavor_create(request, name):
    flavor = dummymodels.Flavor(name=name)
    flavor.save()


def flavor_update(request, flavor_id, name):
    flavor = dummymodels.Flavor.objects.get(id=flavor_id)
    flavor.name = name
    flavor.save()
    return Flavor(flavor)


def flavor_delete(request, flavor_id):
    dummymodels.Flavor.objects.get(id=flavor_id).delete()


def rack_create(request, name, resource_class_id):
    rack = dummymodels.Rack(name=name,
                            resource_class_id=resource_class_id)
    rack.save()


def rack_list(request):
    return [Rack(r) for r in dummymodels.Rack.objects.all()]


def rack_get(request, rack_id):
    return Rack(dummymodels.Rack.objects.get(id=rack_id))


def rack_delete(request, rack_id):
    dummymodels.Rack.objects.get(id=rack_id).delete()
