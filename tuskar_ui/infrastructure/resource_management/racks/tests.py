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

import base64
import tempfile


class RackViewTests(test.BaseAdminViewTests):
    index_page = urlresolvers.reverse(
        'horizon:infrastructure:resource_management:index')

    index_page_racks_tab = (urlresolvers.reverse(
        'horizon:infrastructure:resource_management:index') +
        "?tab=resource_management_tabs__racks_tab")

    @test.create_stubs({tuskar.ResourceClass: ('list',)})
    def test_create_rack_get(self):
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:create')
        rack = self.client.get(url)

        self.assertEqual(rack.status_code, 200)
        self.assertTemplateUsed(rack,
                                'infrastructure/_workflow_base.html')

    # FIXME (mawagner) - After moving EditRack to use workflows, we need
    # to circle back and fix these tests.
    #
    @test.create_stubs({tuskar.Rack: ('list', 'create',),
                        tuskar.ResourceClass: ('list',),
                        tuskar.BaremetalNode: ('create',)})
    def test_create_rack_post(self):
        baremetal_node = self.baremetal_nodes.first()

        tuskar.Rack.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_racks.list())
        tuskar.BaremetalNode.create(
            mox.IsA(http.HttpRequest),
            service_host='New Node',
            cpus=1,
            memory_mb=1024,
            local_gb=10,
            prov_mac_address='AA:BB:CC:DD:EE:FF',
            pm_address=u'',
            pm_user=u'',
            pm_password=u'',
            terminal_port=None).AndReturn(baremetal_node)
        tuskar.Rack.create(
            mox.IsA(http.HttpRequest),
            name='New Rack',
            resource_class_id=u'1',
            location='Tokyo',
            subnet='1.2.3.4/24',
            baremetal_nodes=[{'id': '11'}]).AndReturn(None)
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        data = {
            'name': 'New Rack',
            'resource_class_id': u'1',
            'location': 'Tokyo',
            'subnet': '1.2.3.4/24',
            'nodes-TOTAL_FORMS': 1,
            'nodes-INITIAL_FORMS': 0,
            'nodes-MAX_NUM_FORMS': 1024,
            'nodes-0-service_host': 'New Node',
            'nodes-0-mac_address': 'aa:bb:cc:dd:ee:ff',
            'nodes-0-cpus': u'1',
            'nodes-0-memory_mb': u'1024',
            'nodes-0-local_gb': u'10',
        }
        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:create')
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(resp, self.index_page_racks_tab)

    @test.create_stubs({tuskar.Rack: ('get', 'list_tuskar_nodes'),
                        tuskar.ResourceClass: ('list',)})
    def test_edit_rack_get(self):
        rack = self.tuskar_racks.first()

        tuskar.Rack.get(
            mox.IsA(http.HttpRequest), rack.id).AndReturn(rack)
        tuskar.Rack.list_tuskar_nodes = []
        tuskar.Rack.get(mox.IsA(http.HttpRequest), rack.id).AndReturn(rack)
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:edit', args=[1])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'infrastructure/_workflow_base.html')

    @test.create_stubs({
        tuskar.Rack: ('get', 'list', 'update', 'list_tuskar_nodes'),
        tuskar.ResourceClass: ('list',),
    })
    def test_edit_rack_post(self):
        rack = self.tuskar_racks.first()

        rack_data = {
            'name': 'Updated Rack',
            'resource_class_id': u'1',
            'rack_id': u'1',
            'location': 'New Location',
            'subnet': '127.10.10.0/24',
            'baremetal_nodes': [],
        }

        data = {
            'name': 'Updated Rack',
            'resource_class_id': u'1',
            'rack_id': u'1',
            'location': 'New Location',
            'subnet': '127.10.10.0/24',
            'nodes-TOTAL_FORMS': 0,
            'nodes-INITIAL_FORMS': 0,
            'nodes-MAX_NUM_FORMS': 1024,
        }

        tuskar.Rack.get(
            mox.IsA(http.HttpRequest), rack.id).AndReturn(rack)
        tuskar.Rack.list_tuskar_nodes = []
        tuskar.Rack.get(
            mox.IsA(http.HttpRequest), rack.id).AndReturn(rack)
        tuskar.Rack.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_racks.list())
        tuskar.Rack.update(mox.IsA(http.HttpRequest), rack.id, rack_data)
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:edit',
                                   args=[rack.id])
        response = self.client.post(url, data)
        self.assertNoFormErrors(response)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(response, self.index_page_racks_tab)

    @test.create_stubs({tuskar.Rack: ('get',)})
    def test_edit_status_rack_get(self):
        rack = self.tuskar_racks.first()

        tuskar.Rack.\
            get(mox.IsA(http.HttpRequest), rack.id).\
            AndReturn(rack)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:edit_status',
                                   args=[rack.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(
            res,
            'infrastructure/resource_management/racks/edit_status.html')

    @test.create_stubs({tuskar.Rack: ('get', 'update')})
    def test_edit_status_update_rack_post(self):
        rack = self.tuskar_racks.first()

        tuskar.Rack.\
            get(mox.IsA(http.HttpRequest), rack.id).\
            AndReturn(rack)
        tuskar.Rack.update(mox.IsA(http.HttpRequest), rack.id,
                           {'state': 'active'}).AndReturn(rack)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:edit_status',
                                   args=[rack.id]) + "?action=start"
        response = self.client.post(url)

        self.assertNoFormErrors(response)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(response, self.index_page)

    @test.create_stubs({tuskar.Rack: ('delete', 'list')})
    def test_delete_rack(self):
        rack_id = u'1'
        tuskar.Rack.delete(
            mox.IsA(http.HttpRequest), rack_id).AndReturn(None)
        tuskar.Rack.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_racks.list())

        self.mox.ReplayAll()
        data = {'action': 'racks__delete__%s' % rack_id}
        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:index')
        result = self.client.post(url, data)
        self.assertRedirectsNoFollow(result, self.index_page)

    def test_upload_rack_get(self):
        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:upload')
        rack = self.client.get(url)

        self.assertEqual(rack.status_code, 200)
        self.assertTemplateUsed(
            rack, 'infrastructure/resource_management/racks/upload.html')

    def test_upload_rack_upload(self):
        csv_data = ('Rack1,rclass1,192.168.111.0/24,regionX,f0:dd:f1:da:f9:b5 '
                    'f2:de:f1:da:f9:66 f2:de:ff:da:f9:67')
        temp_file = tempfile.TemporaryFile()
        temp_file.write(csv_data)
        temp_file.flush()
        temp_file.seek(0)

        data = {'csv_file': temp_file, 'upload': '1'}
        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:upload')
        resp = self.client.post(url, data)
        self.assertTemplateUsed(
            resp, 'infrastructure/resource_management/racks/upload.html')
        self.assertNoFormErrors(resp)
        self.assertEqual(resp.context['form']['uploaded_data'].value(),
                         base64.b64encode(csv_data))

    def test_upload_rack_upload_with_error(self):
        data = {'upload': '1'}
        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:upload')
        resp = self.client.post(url, data)
        self.assertTemplateUsed(
            resp, 'infrastructure/resource_management/racks/upload.html')
        self.assertFormErrors(resp, 1)
        self.assertEqual(resp.context['form']['uploaded_data'].value(),
                         None)

    @test.create_stubs({tuskar.Rack: ('create',),
                        tuskar.ResourceClass: ('list',)})
    def test_upload_rack_create(self):
        tuskar.Rack.create(mox.IsA(http.HttpRequest),
                           name='Rack1',
                           resource_class_id='1',
                           location='regionX',
                           subnet='192.168.111.0/24').AndReturn(None)
        tuskar.ResourceClass.list(
            mox.IsA(http.HttpRequest)).AndReturn(
                self.tuskar_resource_classes.list())
        self.mox.ReplayAll()
        csv_data = ('Rack1,rclass1,192.168.111.0/24,regionX,f0:dd:f1:da:f9:b5 '
                    'f2:de:f1:da:f9:66 f2:de:ff:da:f9:67')

        data = {'uploaded_data': base64.b64encode(csv_data), 'add_racks': '1'}
        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:upload')
        resp = self.client.post(url, data)
        self.assertRedirectsNoFollow(resp, self.index_page)
        self.assertMessageCount(success=1)
        self.assertMessageCount(error=0)

    @test.create_stubs({
        tuskar.Rack: ('get', 'list_tuskar_nodes', 'list_flavors'),
        tuskar.ResourceClass: ('get',),
    })
    def test_detail_rack(self):
        rack = self.tuskar_racks.first()
        rack.request = self.request
        resource_class = self.tuskar_resource_classes.first()

        tuskar.Rack.get(mox.IsA(http.HttpRequest),
                        rack.id).AndReturn(rack)
        tuskar.ResourceClass.get(mox.IsA(http.HttpRequest),
                                 resource_class.id).AndReturn(resource_class)
        self.mox.ReplayAll()

        tuskar.Rack.list_tuskar_nodes = []
        tuskar.Rack.list_flavors = []

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:detail',
                                   args=[rack.id])
        res = self.client.get(url)
        self.assertTemplateUsed(res, "infrastructure/resource_management/"
                                     "racks/detail.html")

    # FIXME: test actual json output once we stop using mock data
    def test_usage_data_rack(self):
        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:usage_data')
        res = self.client.get(url)
        self.assertEquals(res['Content-Type'], 'application/json')

    # FIXME: test actual json output once we stop using mock data
    @test.create_stubs({tuskar.Rack: ('get',)})
    def test_top_communicating_rack(self):
        rack = self.tuskar_racks.first()

        tuskar.Rack.get(mox.IsA(http.HttpRequest),
                        rack.id).AndReturn(rack)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:'
                                   'top_communicating', args=[rack.id])
        res = self.client.get(url)
        self.assertEquals(res['Content-Type'], 'application/json')

    # FIXME: test actual json output once we stop using mock data
    @test.create_stubs({tuskar.Rack: ('get',)})
    def test_node_health_rack(self):
        rack = self.tuskar_racks.first()

        tuskar.Rack.get(mox.IsA(http.HttpRequest),
                        rack.id).AndReturn(rack)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:'
                                   'node_health', args=[rack.id])
        res = self.client.get(url)
        self.assertEquals(res['Content-Type'], 'application/json')

    @test.create_stubs({tuskar.Rack: ('get',)})
    def test_check_state_rack(self):
        rack = self.tuskar_racks.first()

        tuskar.Rack.get(mox.IsA(http.HttpRequest),
                        rack.id).AndReturn(rack)

        self.mox.ReplayAll()

        url = urlresolvers.reverse('horizon:infrastructure:'
                                   'resource_management:racks:'
                                   'check_state', args=[rack.id])
        res = self.client.get(url)
        state_json = '{"state": "active"}'

        self.assertEquals(res['Content-Type'], 'application/json')
        self.assertEquals(res.content, state_json)

    @test.create_stubs({
        tuskar.Rack: ('get', 'list_baremetal_nodes', 'update',
                      'list_tuskar_nodes'),
        tuskar.BaremetalNode: ('get',),
        tuskar.TuskarNode: ('list',),
    })
    def test_node_delete(self):
        rack = self.tuskar_racks.first()
        rack.request = self.request
        baremetal_nodes = self.baremetal_nodes.list()
        baremetal_node = baremetal_nodes[0]
        baremetal_node.request = self.request
        tuskar_nodes = self.tuskar_nodes.list()

        tuskar.Rack.get(mox.IsA(http.HttpRequest), rack.id).AndReturn(rack)
        tuskar.BaremetalNode.get(mox.IsA(http.HttpRequest),
                                 baremetal_node.id).AndReturn(baremetal_node)
        tuskar.TuskarNode.list(
            mox.IsA(http.HttpRequest)).AndReturn(tuskar_nodes)
        tuskar.Rack.get(None, rack.id).AndReturn(rack)  # called by node.rack
        tuskar.Rack.update(mox.IsA(http.HttpRequest), rack.id, {
            'baremetal_nodes': [{'id': node.id}
                                for node in baremetal_nodes
                                if node.id != baremetal_node.id],
        }).AndReturn(rack)

        tuskar.Rack.list_baremetal_nodes = baremetal_nodes
        tuskar.Rack.list_tuskar_nodes = tuskar_nodes
        self.mox.ReplayAll()

        url = urlresolvers.reverse(
            'horizon:infrastructure:resource_management:racks:detail',
            args=[rack.id])
        form_data = {'action': 'nodes_table__delete__%s' % baremetal_node.id}
        response = self.client.post(url, form_data)
        self.assertNoFormErrors(response)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(response, url)
