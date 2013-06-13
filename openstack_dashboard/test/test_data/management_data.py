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

from openstack_dashboard.api.management import Flavor, ResourceClass

import openstack_dashboard.dashboards.infrastructure.models as dummymodels

from .utils import TestDataContainer


def data(TEST):
    TEST.management_flavors = TestDataContainer()

    # Flavors
    flavor_1 = Flavor(dummymodels.Flavor(
            id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            name='m1.tiny'))
    flavor_2 = Flavor(dummymodels.Flavor(
            id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            name='m1.massive'))
    TEST.management_flavors.add(flavor_1, flavor_2)

    # Resource Classes
    TEST.management_resource_classes = TestDataContainer()

    resource_class_1 = ResourceClass({
        "id": "1",
        "model": "infrastructure.resourceclass",
        "fields": {"service_type": "compute",
        "flavors": ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"],
        "name": "rclass1"}})

    resource_class_2 = ResourceClass({
        "id": "2",
        "model": "infrastructure.resourceclass",
        "fields": {"service_type": "compute",
        "flavors": [],
        "name": "rclass2"}})

    TEST.management_resource_classes.add(resource_class_1, resource_class_2)
