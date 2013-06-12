# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
#
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

# FIXME: configuration for dummy data
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Capacity(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    name = models.CharField(max_length=50)
    value = models.PositiveIntegerField()
    unit = models.CharField(max_length=10)


class Flavor(models.Model):
    class Meta:
        db_table = 'infrastructure_flavor'

    name = models.CharField(max_length=50, unique=True)
    capacities = generic.GenericRelation(Capacity)


class Host(models.Model):
    class Meta:
        db_table = 'infrastructure_host'

    name = models.CharField(max_length=50, unique=True)
    rack = models.ForeignKey('Rack')
    capacities = generic.GenericRelation(Capacity)


class Rack(models.Model):
    class Meta:
        db_table = 'infrastructure_rack'

    name = models.CharField(max_length=50, unique=True)
    resource_class = models.ForeignKey('ResourceClass')
    capacities = generic.GenericRelation(Capacity)


class ResourceClass(models.Model):
    class Meta:
        # syncdb by default creates 'openstack_dashboard_resourceclass' table,
        # but it's better to keep models under
        # openstack_dashboard/dashboards/infrastructure/models.py instead of
        # openstack_dashboard/models.py since the models.py stub file is
        # required here anyway
        db_table = 'infrastructure_resourceclass'

    name = models.CharField(max_length=50, unique=True)
    service_type = models.CharField(max_length=50)
    status = models.CharField(max_length=10, null=True, blank=True)


class ResourceClassFlavor(models.Model):
    class Meta:
        db_table = 'infrastructure_resourceclass_flavors'

    flavor = models.ForeignKey('Flavor')
    resource_class = models.ForeignKey('ResourceClass')
    max_vms = models.PositiveIntegerField()
