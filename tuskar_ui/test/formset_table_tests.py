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

import django.forms

from horizon import tables
import tuskar_ui.tables
from tuskar_ui.test import helpers as test


class FormsetTableTests(test.TestCase):

    def test_populate(self):
        """Create a FormsetDataTable and populate it with data."""

        class TableObj(object):
            pass

        obj = TableObj()
        obj.name = 'test object'
        obj.value = 42
        obj.id = 4

        class TableForm(django.forms.Form):
            name = django.forms.CharField()
            value = django.forms.IntegerField()

        TableFormset = django.forms.formsets.formset_factory(TableForm,
                                                             extra=0)

        class Table(tuskar_ui.tables.FormsetDataTable):
            formset_class = TableFormset

            name = tables.Column('name')
            value = tables.Column('value')

            class Meta:
                name = 'table'

        table = Table(self.request)
        table.data = [obj]
        formset = table.get_formset()
        self.assertEqual(len(formset), 1)
        form = formset[0]
        form_data = form.initial
        self.assertEqual(form_data['name'], 'test object')
        self.assertEqual(form_data['value'], 42)
