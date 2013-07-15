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
from mox import IsA, IgnoreArg
from django import http
import tempfile
import base64
from django.core.files.uploadedfile import InMemoryUploadedFile


class RackViewTests(test.BaseAdminViewTests):
    index_page = reverse('horizon:infrastructure:resource_management:index')

    def test_create_rack_get(self):
        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:create')
        rack = self.client.get(url)

        self.assertEqual(rack.status_code, 200)
        self.assertTemplateUsed(rack,
                                'horizon/common/_workflow_base.html')

    # FIXME (mawagner) - After moving EditRack to use workflows, we need
    # to circle back and fix these tests.
    #
    @test.create_stubs({api.tuskar.Rack: ('create',)})
    def test_create_rack_post(self):
        api.tuskar.Rack.create(IsA(http.request.HttpRequest), 'New Rack',
                                   u'2', 'Tokyo', '1.2.3.4').AndReturn(None)
        self.mox.ReplayAll()

        data = {'name': 'New Rack', 'resource_class_id': u'2',
                'location': 'Tokyo', 'subnet': '1.2.3.4'}
        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:create')
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(resp, self.index_page)

    def test_edit_rack_get(self):
        url = reverse('horizon:infrastructure:resource_management:' +
                      'racks:edit', args=[1])
        rack = self.client.get(url)
        self.assertEqual(rack.status_code, 200)
        self.assertTemplateUsed(rack,
                                'horizon/common/_workflow_base.html')

    @test.create_stubs({api.tuskar.Rack: ('update',)})
    def test_edit_rack_post(self):
        data = {'name': 'Updated Rack', 'resource_class_id': u'1',
                'rack_id': u'1', 'location': 'New Location',
                'subnet': '127.10.10.0/24', 'node_macs': 'foo'}

        api.tuskar.Rack.update(u'1', data)
        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:' +
                      'racks:edit', args=[1])
        response = self.client.post(url, data)
        self.assertNoFormErrors(response)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(response, self.index_page)

    @test.create_stubs({api.tuskar.Rack: ('delete',)})
    def test_delete_rack(self):
        rack_id = u'1'
        api.tuskar.Rack.delete(IsA(http.request.HttpRequest), rack_id) \
                                   .AndReturn(None)
        self.mox.ReplayAll()
        data = {'action': 'racks__delete__%s' % rack_id}
        url = reverse('horizon:infrastructure:resource_management:index')
        result = self.client.post(url, data)
        self.assertRedirectsNoFollow(result, self.index_page)

    def test_upload_rack_get(self):
        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:upload')
        rack = self.client.get(url)

        self.assertEqual(rack.status_code, 200)
        self.assertTemplateUsed(rack,
            'infrastructure/resource_management/racks/upload.html')

    def test_upload_rack_upload(self):
        csv_data = 'Rack1,rclass1,192.168.111.0/24,regionX,f0:dd:f1:da:f9:b5 '\
                   'f2:de:f1:da:f9:66 f2:de:ff:da:f9:67'
        temp_file = tempfile.TemporaryFile()
        temp_file.write(csv_data)
        temp_file.flush()
        temp_file.seek(0)

        data = {'csv_file': temp_file, 'upload': '1'}
        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:upload')
        resp = self.client.post(url, data)
        self.assertTemplateUsed(resp,
            'infrastructure/resource_management/racks/upload.html')
        self.assertNoFormErrors(resp)
        self.assertEqual(resp.context['form']['uploaded_data'].value(),
            base64.b64encode(csv_data))

    def test_upload_rack_upload_with_error(self):
        data = {'upload': '1'}
        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:upload')
        resp = self.client.post(url, data)
        self.assertTemplateUsed(resp,
            'infrastructure/resource_management/racks/upload.html')
        self.assertFormErrors(resp, 1)
        self.assertEqual(resp.context['form']['uploaded_data'].value(),
            None)

    @test.create_stubs({api.tuskar.Rack: ('create', 'register_nodes'),
                        api.tuskar.ResourceClass: ('list',)})
    def test_upload_rack_create(self):
        api.tuskar.Rack.create(IsA(http.request.HttpRequest), 'Rack1',
            '1', 'regionX', '192.168.111.0/24').AndReturn(None)
        api.tuskar.Rack.register_nodes(IgnoreArg(),
            IgnoreArg()).AndReturn(None)
        api.tuskar.ResourceClass.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        self.mox.ReplayAll()
        csv_data = 'Rack1,rclass1,192.168.111.0/24,regionX,f0:dd:f1:da:f9:b5 '\
                   'f2:de:f1:da:f9:66 f2:de:ff:da:f9:67'

        data = {'uploaded_data': base64.b64encode(csv_data), 'add_racks': '1'}
        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:upload')
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(resp, self.index_page)
        self.assertMessageCount(success=1)
        self.assertMessageCount(error=0)
