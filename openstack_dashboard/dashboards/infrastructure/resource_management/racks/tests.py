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

from django.core.urlresolvers import reverse
from openstack_dashboard.test import helpers as test
from openstack_dashboard import api
from mox import IsA
from django import http


class ResourceViewTests(test.BaseAdminViewTests):
    index_page = reverse('horizon:infrastructure:resource_management:index')

    @test.create_stubs({api.management.Rack: ('create',), })
    def test_create_rack(self):
        api.management.Rack.create(IsA(http.request.HttpRequest), 'New Rack',
                                   u'2').AndReturn(None)
        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:create')
        resource = self.client.get(url)

        self.assertEqual(resource.status_code, 200)
        self.assertTemplateUsed(resource,
                                'infrastructure/resource_management/racks/' +
                                'create.html')

        data = {'name': 'New Rack', 'resource_class_id': u'2'}
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(resp, self.index_page)

    # FIXME: The 'edit' action currently has no API call
    def test_edit_rack(self):
        url = reverse('horizon:infrastructure:resource_management:' +
                      'racks:edit', args=[1])
        resource = self.client.get(url)
        self.assertEqual(resource.status_code, 200)
        self.assertTemplateUsed(resource,
                                'infrastructure/resource_management/racks/' +
                                'edit.html')

        data = {'name': 'Updated Rack', 'resource_class_id': 1, 'rack_id': 1}
        response = self.client.post(url, data)
        self.assertNoFormErrors(response)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(response, self.index_page)

    @test.create_stubs({api.management.Rack: ('delete',)})
    def test_delete_rack(self):
        rack_id = u'1'
        api.management.Rack.delete(IsA(http.request.HttpRequest), rack_id) \
                                   .AndReturn(None)
        self.mox.ReplayAll()
        data = {'action': 'racks__delete__%s' % rack_id}
        url = reverse('horizon:infrastructure:resource_management:index')
        result = self.client.post(url, data)
        self.assertRedirectsNoFollow(result, self.index_page)
