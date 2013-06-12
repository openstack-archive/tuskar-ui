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

from collections import namedtuple
from django import http
from django.core.urlresolvers import reverse
from mox import IsA
from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


class ResourceClassesTests(test.BaseAdminViewTests):
    def test_create_resource_class(self):
        ResourceClass = namedtuple('ResourceClass', 'id, name, service_type')
        resource_class = ResourceClass(1, 'test', 'compute')

        self.mox.ReplayAll()
        url = reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = {'name': resource_class.name,
                'service_type': resource_class.service_type}
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(
            resp, reverse('horizon:infrastructure:resource_management:index'))

    def test_edit_resource_class(self):
        ResourceClass = namedtuple('ResourceClass', 'id, name, service_type')
        resource_class = ResourceClass(1, 'test', 'compute')
        self.mox.ReplayAll()
        # get_test
        url = reverse(
            'horizon:infrastructure:resource_management:'
            'resource_classes:update',
            args=[resource_class.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # post test
        data = {'resource_class_id': resource_class.id,
                'name': resource_class.name,
                'service_type': resource_class.service_type}
        resp = self.client.post(url, data)
        self.assertNoFormErrors(resp)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(
            resp, reverse('horizon:infrastructure:resource_management:index'))

    """ #I don't have update yet, it's not suported by API """

    def test_delete_resource_class(self):
        ResourceClass = namedtuple('ResourceClass', 'id, name, service_type')
        resource_class = ResourceClass(1, 'test', 'compute')
        self.mox.ReplayAll()
        form_data = {'action':
                        'resource_classes__delete__%s' % resource_class.id}
        res = self.client.post(
            reverse('horizon:infrastructure:resource_management:index'),
            form_data)
        self.assertRedirectsNoFollow(
            res, reverse('horizon:infrastructure:resource_management:index'))


class ResourceClassViewTests(test.BaseAdminViewTests):

    def test_detail_get(self):
        ResourceClass = namedtuple('ResourceClass', 'id, name,  service_type')
        resource_class = ResourceClass('1', 'test', 'compute')

        url = reverse('horizon:infrastructure:resource_management:'
                      'resource_classes:detail', args=[resource_class.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(
            res, 'infrastructure/resource_management/resource_classes/'
                 'detail.html')

    # def test_detail_get_exception(self):
    #     index_url = reverse('horizon:infractructure:resource_management:'
    #                         'resource_classes:index')
    #     detail_url = reverse('horizon:infrastructure:resource_management:'
    #                          'resource_classes:detail', args=[42])

    #     res = self.client.get(detail_url)
    #     self.assertRedirectsNoFollow(res, index_url)
