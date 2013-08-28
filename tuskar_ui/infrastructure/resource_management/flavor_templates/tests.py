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


class FlavorTemplatesTests(test.BaseAdminViewTests):

    @test.create_stubs({tuskar.FlavorTemplate: ('list', 'create')})
    def test_create_flavor_template(self):
        template = self.tuskar_flavor_templates.first()

        tuskar.FlavorTemplate.list(
            mox.IsA(http.HttpRequest)).AndReturn([])
        tuskar.FlavorTemplate.create(mox.IsA(http.HttpRequest),
                                     name=template.name,
                                     cpu=0,
                                     memory=0,
                                     storage=0,
                                     ephemeral_disk=0,
                                     swap_disk=0).AndReturn(template)
        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                        'resource_management:flavor_templates:'
                                        'create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'infrastructure/resource_management/'
                                      'flavor_templates/create.html')

        data = {'name': template.name,
                'cpu': 0,
                'memory': 0,
                'storage': 0,
                'ephemeral_disk': 0,
                'swap_disk': 0}
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(resp,
            urlresolvers.reverse('horizon:infrastructure:resource_management:'
                                    'index'))

    @test.create_stubs({tuskar.FlavorTemplate: ('list', 'create')})
    def test_create_flavor_template_post_exception(self):
        template = self.tuskar_flavor_templates.first()

        tuskar.FlavorTemplate.list(
            mox.IsA(http.HttpRequest)).AndReturn([])
        tuskar.FlavorTemplate.create(
            mox.IsA(http.HttpRequest),
            name=template.name,
            cpu=0,
            memory=0,
            storage=0,
            ephemeral_disk=0,
            swap_disk=0).AndRaise(self.exceptions.tuskar)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                        'resource_management:flavor_templates:'
                                        'create')
        data = {'name': template.name,
                'cpu': 0,
                'memory': 0,
                'storage': 0,
                'ephemeral_disk': 0,
                'swap_disk': 0}
        resp = self.client.post(url, data)

        self.assertMessageCount(resp, error=1)

    @test.create_stubs({tuskar.FlavorTemplate: ('list', 'update', 'get')})
    def test_edit_flavor_template_get(self):
        template = self.tuskar_flavor_templates.first()  # has no extra spec

        tuskar.FlavorTemplate.get(mox.IsA(http.HttpRequest),
                                  template.id).AndReturn(template)
        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                        'resource_management:flavor_templates:'
                                        'edit',
                                   args=[template.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "infrastructure/resource_management/"
                                      "flavor_templates/edit.html")

    @test.create_stubs({tuskar.FlavorTemplate: ('list', 'update', 'get')})
    def test_edit_flavor_template_post(self):
        template = self.tuskar_flavor_templates.first()  # has no extra spec

        tuskar.FlavorTemplate.list(mox.IsA(http.HttpRequest)).AndReturn(
            self.tuskar_flavor_templates.list())
        tuskar.FlavorTemplate.update(mox.IsA(http.HttpRequest),
                                     template_id=template.id,
                                     name=template.name,
                                     cpu=0,
                                     memory=0,
                                     storage=0,
                                     ephemeral_disk=0,
                                     swap_disk=0).AndReturn(template)
        tuskar.FlavorTemplate.get(mox.IsA(http.HttpRequest),
                                  template.id).AndReturn(template)
        self.mox.ReplayAll()

        data = {'flavor_template_id': template.id,
                'name': template.name,
                'cpu': 0,
                'memory': 0,
                'storage': 0,
                'ephemeral_disk': 0,
                'swap_disk': 0}
        url = urlresolvers.reverse('horizon:infrastructure:'
                                        'resource_management:flavor_templates:'
                                        'edit',
                                   args=[template.id])
        resp = self.client.post(url, data)
        self.assertNoFormErrors(resp)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(resp,
            urlresolvers.reverse('horizon:infrastructure:resource_management:'
                                        'index'))

    @test.create_stubs({tuskar.FlavorTemplate: ('list', 'update')})
    def test_edit_flavor_template_post_exception(self):
        template = self.tuskar_flavor_templates.first()  # has no extra spec

        tuskar.FlavorTemplate.list(mox.IsA(http.HttpRequest)).AndReturn(
            self.tuskar_flavor_templates.list())
        tuskar.FlavorTemplate.update(
            mox.IsA(http.HttpRequest),
            template_id=template.id,
            name=template.name,
            cpu=0,
            memory=0,
            storage=0,
            ephemeral_disk=0,
            swap_disk=0).AndRaise(self.exceptions.tuskar)
        self.mox.ReplayAll()

        data = {'flavor_template_id': template.id,
                'name': template.name,
                'cpu': 0,
                'memory': 0,
                'storage': 0,
                'ephemeral_disk': 0,
                'swap_disk': 0}
        url = urlresolvers.reverse('horizon:infrastructure:'
                                        'resource_management:flavor_templates:'
                                        'edit',
                                   args=[template.id])
        resp = self.client.post(url, data)

        self.assertMessageCount(resp, error=1)

    @test.create_stubs({tuskar.FlavorTemplate: ('list', 'delete')})
    def test_delete_flavor_template(self):
        template = self.tuskar_flavor_templates.first()

        tuskar.FlavorTemplate.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_flavor_templates.list())
        tuskar.FlavorTemplate.delete(mox.IsA(http.HttpRequest), template.id)
        self.mox.ReplayAll()

        form_data = {'action': 'flavor_templates__delete__%s' % template.id}
        res = self.client.post(
            urlresolvers.reverse('horizon:infrastructure:resource_management:'
                                    'index'),
            form_data)

        self.assertRedirectsNoFollow(res,
            urlresolvers.reverse('horizon:infrastructure:resource_management:'
                                    'index'))

    @test.create_stubs({tuskar.FlavorTemplate: ('get',)})
    def test_detail_flavor_template(self):
        template = self.tuskar_flavor_templates.first()

        tuskar.FlavorTemplate.get(mox.IsA(http.HttpRequest),
                                  template.id).AndReturn(template)
        tuskar.FlavorTemplate.resource_classes = self. \
            tuskar_resource_classes

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                        'resource_management:flavor_templates:'
                                        'detail',
                                   args=[template.id])
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'infrastructure/resource_management/'
                                     'flavor_templates/detail.html')

    @test.create_stubs({tuskar.FlavorTemplate: ('get',)})
    def test_detail_flavor_template_exception(self):
        template = self.tuskar_flavor_templates.first()

        tuskar.FlavorTemplate.get(
            mox.IsA(http.HttpRequest), template.id).AndRaise(
                self.exceptions.tuskar)
        tuskar.FlavorTemplate.resource_classes = self.tuskar_resource_classes

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                        'resource_management:flavor_templates:'
                                        'detail',
                                   args=[template.id])
        res = self.client.get(url)

        self.assertRedirectsNoFollow(res,
            urlresolvers.reverse('horizon:infrastructure:resource_management:'
                                    'index'))
