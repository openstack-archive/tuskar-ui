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
from django import http

from mox import IsA

from tuskar_ui import api as tuskar
from tuskar_ui.test import helpers as test

import base64
import tempfile


class RackViewTests(test.BaseAdminViewTests):
    index_page = reverse('horizon:infrastructure:resource_management:index')

    @test.create_stubs({tuskar.ResourceClass: ('list',)})
    def test_create_rack_get(self):
        tuskar.ResourceClass.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:create')
        rack = self.client.get(url)

        self.assertEqual(rack.status_code, 200)
        self.assertTemplateUsed(rack,
                                'horizon/common/_workflow_base.html')

    # FIXME (mawagner) - After moving EditRack to use workflows, we need
    # to circle back and fix these tests.
    #
    @test.create_stubs({tuskar.Rack: ('list', 'create',),
                        tuskar.ResourceClass: ('list',),
                        tuskar.Node: ('create',)})
    def test_create_rack_post(self):
        node = self.baremetal_nodes.first()

        tuskar.Rack.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_racks.list())
        tuskar.Node.create(
            IsA(http.request.HttpRequest),
            name='New Node',
            cpus=u'1',
            memory_mb=u'1024',
            local_gb=u'10',
            prov_mac_address='aa:bb:cc:dd:ee',
            pm_address=u'',
            pm_user=u'',
            pm_password=u'',
            terminal_port=u'').AndReturn(node)
        tuskar.Rack.create(
            IsA(http.request.HttpRequest),
            name='New Rack',
            resource_class_id=u'1',
            location='Tokyo',
            subnet='1.2.3.4',
            nodes=[{'id': '1'}]).AndReturn(None)
        tuskar.ResourceClass.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        data = {'name': 'New Rack', 'resource_class_id': u'1',
                'location': 'Tokyo', 'subnet': '1.2.3.4',
                'node_name': 'New Node', 'prov_mac_address': 'aa:bb:cc:dd:ee',
                'cpus': u'1', 'memory_mb': u'1024', 'local_gb': u'10'}
        url = reverse('horizon:infrastructure:resource_management:'
                      'racks:create')
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(resp, self.index_page)

    @test.create_stubs({tuskar.Rack: ('get', 'list_nodes'),
                        tuskar.ResourceClass: ('list',)})
    def test_edit_rack_get(self):
        rack = self.tuskar_racks.first()

        tuskar.Rack.\
            get(IsA(http.HttpRequest), rack.id).\
            MultipleTimes().AndReturn(rack)
        tuskar.ResourceClass.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        tuskar.Rack.list_nodes = []

        url = reverse('horizon:infrastructure:resource_management:' +
                      'racks:edit', args=[1])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'horizon/common/_workflow_base.html')

    @test.create_stubs({tuskar.Rack: ('get', 'list', 'update',),
                        tuskar.ResourceClass: ('list',)})
    def test_edit_rack_post(self):
        rack = self.tuskar_racks.first()

        rack_data = {'name': 'Updated Rack', 'resource_class_id': u'1',
                'rack_id': u'1', 'location': 'New Location',
                     'subnet': '127.10.10.0/24', 'node_macs': None}

        data = {'name': 'Updated Rack', 'resource_class_id': u'1',
                'rack_id': u'1', 'location': 'New Location',
                'subnet': '127.10.10.0/24', 'node_macs': None,
                'node_name': 'New Node', 'prov_mac_address': 'aa:bb:cc:dd:ee',
                'cpus': u'1', 'memory_mb': u'1024', 'local_gb': u'10'}

        tuskar.Rack.get(
            IsA(http.HttpRequest), rack.id).MultipleTimes().\
            AndReturn(rack)
        tuskar.Rack.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_racks.list())
        tuskar.Rack.update(IsA(http.HttpRequest), rack.id, rack_data)
        tuskar.ResourceClass.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        url = reverse('horizon:infrastructure:resource_management:' +
                      'racks:edit', args=[rack.id])
        response = self.client.post(url, data)
        self.assertNoFormErrors(response)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(response, self.index_page)

    @test.create_stubs({tuskar.Rack: ('delete', 'list')})
    def test_delete_rack(self):
        rack_id = u'1'
        tuskar.Rack.delete(IsA(http.request.HttpRequest), rack_id) \
                                   .AndReturn(None)
        tuskar.Rack.list(
            IsA(http.request.HttpRequest)).AndReturn(
                self.tuskar_racks.list())

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

    @test.create_stubs({tuskar.Rack: ('create',),
                        tuskar.ResourceClass: ('list',)})
    def test_upload_rack_create(self):
        tuskar.Rack.create(IsA(http.request.HttpRequest),
                name='Rack1',
                resource_class_id='1',
                location='regionX',
                subnet='192.168.111.0/24').AndReturn(None)
        tuskar.ResourceClass.list(
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
