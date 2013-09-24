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

from django import forms
from django.utils import datastructures
from django.utils import html

from horizon import conf
from horizon.tables import base as horizon_tables


STRING_SEPARATOR = "__"


# FIXME: Remove this class and use Row directly after it becomes easier to
# extend it, see bug #1229677
class BaseRow(horizon_tables.Row):
    """
    A DataTable Row class that is easier to extend.

    All of this code is lifted from ``horizon_tables.Row`` and just split into
    two separate methods, so that it is possible to override one of them
    without touching the code of the other.
    """

    def load_cells(self, datum=None):
        # Compile all the cells on instantiation.
        table = self.table
        if datum:
            self.datum = datum
        else:
            datum = self.datum
        cells = []
        for column in table.columns.values():
            data = self.load_cell_data(column, datum)
            cell = horizon_tables.Cell(datum, data, column, self)
            cells.append((column.name or column.auto, cell))
        self.cells = datastructures.SortedDict(cells)

        if self.ajax:
            interval = conf.HORIZON_CONFIG['ajax_poll_interval']
            self.attrs['data-update-interval'] = interval
            self.attrs['data-update-url'] = self.get_ajax_update_url()
            self.classes.append("ajax-update")

        # Add the row's status class and id to the attributes to be rendered.
        self.classes.append(self.status_class)
        id_vals = {"table": self.table.name,
                   "sep": STRING_SEPARATOR,
                   "id": table.get_object_id(datum)}
        self.id = "%(table)s%(sep)srow%(sep)s%(id)s" % id_vals
        self.attrs['id'] = self.id

        # Add the row's display name if available
        display_name = table.get_object_display(datum)
        if display_name:
            self.attrs['data-display'] = html.escape(display_name)

    def load_cell_data(self, column, datum):
        table = self.table
        if column.auto == "multi_select":
            widget = forms.CheckboxInput(check_test=lambda value: False)
            # Convert value to string to avoid accidental type conversion
            data = widget.render('object_ids',
                                 unicode(table.get_object_id(datum)))
            table._data_cache[column][table.get_object_id(datum)] = data
        elif column.auto == "actions":
            data = table.render_row_actions(datum)
            table._data_cache[column][table.get_object_id(datum)] = data
        else:
            data = column.get_data(datum)
        return data


class MultiselectRow(BaseRow):
    """
    A DataTable Row class that handles pre-selected multi-select checboxes.

    It adds custom code to pre-fill the checkboxes in the multi-select column
    according to provided values, so that the selections can be kept between
    requests.
    """

    def load_cell_data(self, column, datum):
        table = self.table
        if column.auto == "multi_select":
            # multi_select fields in the table must be checked after
            # a server action
            # TODO(remove this ugly code and create proper TableFormWidget)
            multi_select_values = []
            if (getattr(table, 'request', False) and
                    getattr(table.request, 'POST', False)):
                multi_select_values = table.request.POST.getlist(
                        self.table.multi_select_name)

            multi_select_values += getattr(table,
                                           'active_multi_select_values',
                                           [])

            if unicode(table.get_object_id(datum)) in multi_select_values:
                multi_select_value = lambda value: True
            else:
                multi_select_value = lambda value: False
            widget = forms.CheckboxInput(check_test=multi_select_value)

            # Convert value to string to avoid accidental type conversion
            data = widget.render(self.table.multi_select_name,
                                 unicode(table.get_object_id(datum)))
            table._data_cache[column][table.get_object_id(datum)] = data
        else:
            data = super(MultiselectRow, self).load_cell_data(column, datum)
        return data

