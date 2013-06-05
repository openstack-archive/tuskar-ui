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


class Flavor(models.Model):
    class Meta:
        db_table = 'infrastructure_flavor'

    name = models.CharField(max_length=50, unique=True)
    # TODO: proper capacities representation

    def capacities():
        return []


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
    flavors = models.ManyToManyField(Flavor)
