# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from django.core import urlresolvers
from django import http
import mox

from tuskar_ui import api as tuskar
from tuskar_ui.test import helpers as test


class FlavorsTests(test.BaseAdminViewTests):

    @test.create_stubs({tuskar.Flavor: ('get',),
                        tuskar.ResourceClass: ('get',)})
    def test_detail_flavor(self):
        flavor = self.tuskar_flavors.list()[1]
        resource_class = self.tuskar_resource_classes.first()

        tuskar.ResourceClass.get(mox.IsA(http.HttpRequest),
                                 resource_class.id).AndReturn(resource_class)

        tuskar.Flavor.get(mox.IsA(http.HttpRequest),
                          resource_class.id,
                          flavor.id).AndReturn(flavor)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:resource_classes:'
                                   'flavors:detail',
                                   args=[resource_class.id, flavor.id])
        res = self.client.get(url)
        self.assertTemplateUsed(res,
                                'infrastructure/resource_management/'
                                'flavors/detail.html')

    @test.create_stubs({tuskar.Flavor: ('get',)})
    def test_detail_flavor_exception(self):
        flavor = self.tuskar_flavors.list()[1]
        resource_class = self.tuskar_resource_classes.first()

        tuskar.Flavor.get(mox.IsA(http.HttpRequest),
                          resource_class.id,
                          flavor.id).AndRaise(self.exceptions.tuskar)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:resource_classes:'
                                   'flavors:detail',
                                   args=[resource_class.id, flavor.id])
        res = self.client.get(url)

        self.assertRedirectsNoFollow(
            res,
            urlresolvers.reverse('horizon:infrastructure:resource_management:'
                                 'index'))
