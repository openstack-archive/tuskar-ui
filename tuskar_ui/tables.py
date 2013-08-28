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

import copy
import logging
import operator
import sys

from django import forms
import django.http
from django import template
from django.utils import datastructures
from django.utils import html
from django.utils import http
from django.utils import termcolors
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import conf
from horizon import exceptions
from horizon import messages
from horizon.tables import actions as table_actions
from horizon.tables import base as horizon_tables


LOG = logging.getLogger(__name__)
PALETTE = termcolors.PALETTES[termcolors.DEFAULT_PALETTE]
STRING_SEPARATOR = "__"


class Column(horizon_tables.Column):

    def __init__(self, transform, verbose_name=None, sortable=True,
                 link=None, allowed_data_types=[], hidden=False, attrs=None,
                 status=False, status_choices=None, display_choices=None,
                 empty_value=None, filters=None, classes=None, summation=None,
                 auto=None, truncate=None, link_classes=None,
                 # FIXME: Added for TableStep:
                 form_widget=None, form_widget_attributes=None
                 ):
        super(Column, self).__init__(
            transform, verbose_name, sortable, link, allowed_data_types,
            hidden, attrs, status, status_choices, display_choices,
            empty_value, filters, classes, summation, auto, truncate,
            link_classes)

        self.form_widget = form_widget  # FIXME: TableStep
        self.form_widget_attributes = form_widget_attributes or {}  # TableStep


class Row(horizon_tables.Row):

    def load_cells(self, datum=None):
        """
        Load the row's data (either provided at initialization or as an
        argument to this function), initiailize all the cells contained
        by this row, and set the appropriate row properties which require
        the row's data to be determined.

        This function is called automatically by
        :meth:`~horizon.tables.Row.__init__` if the ``datum`` argument is
        provided. However, by not providing the data during initialization
        this function allows for the possibility of a two-step loading
        pattern when you need a row instance but don't yet have the data
        available.
        """
        # Compile all the cells on instantiation.
        table = self.table
        if datum:
            self.datum = datum
        else:
            datum = self.datum
        cells = []
        for column in table.columns.values():
            if column.auto == "multi_select":

                # FIXME: TableStep code modified
                # multi_select fields in the table must be checked after
                # a server action
                # TODO(remove this ugly code and create proper TableFormWidget)
                multi_select_values = []
                if (getattr(table, 'request', False) and
                        getattr(table.request, 'POST', False)):
                    multi_select_values = table.request.POST.getlist(
                            self.table._meta.multi_select_name)

                multi_select_values += getattr(table,
                                               'active_multi_select_values',
                                               [])

                if unicode(table.get_object_id(datum)) in multi_select_values:
                    multi_select_value = lambda value: True
                else:
                    multi_select_value = lambda value: False
                widget = forms.CheckboxInput(check_test=multi_select_value)

                # Convert value to string to avoid accidental type conversion
                data = widget.render(self.table._meta.multi_select_name,
                                     unicode(table.get_object_id(datum)))
                # FIXME: end of added TableStep code

                table._data_cache[column][table.get_object_id(datum)] = data
            elif column.auto == "form_widget":  # FIXME: Added for TableStep:
                widget = column.form_widget
                widget_name = "%s__%s__%s" % \
                    (self.table._meta.multi_select_name,
                     column.name,
                     unicode(table.get_object_id(datum)))

                data = widget.render(widget_name,
                                     column.get_data(datum),
                                     column.form_widget_attributes)
                table._data_cache[column][table.get_object_id(datum)] = data
            elif column.auto == "actions":
                data = table.render_row_actions(datum)
                table._data_cache[column][table.get_object_id(datum)] = data
            else:
                data = column.get_data(datum)
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


class DataTableOptions(horizon_tables.DataTableOptions):

    def __init__(self, options):
        super(DataTableOptions, self).__init__(options)

        # FIXME: TableStep
        self.row_class = getattr(options, 'row_class', Row)
        self.column_class = getattr(options, 'column_class', Column)
        self.multi_select_name = getattr(options,
                                         'multi_select_name',
                                         'object_ids')


class DataTableMetaclass(type):
    """ Metaclass to add options to DataTable class and collect columns. """
    def __new__(mcs, name, bases, attrs):
        # Process options from Meta
        class_name = name
        attrs["_meta"] = opts = DataTableOptions(attrs.get("Meta", None))

        # Gather columns; this prevents the column from being an attribute
        # on the DataTable class and avoids naming conflicts.
        columns = []
        for attr_name, obj in attrs.items():
            if issubclass(type(obj), (opts.column_class, Column)):
                column_instance = attrs.pop(attr_name)
                column_instance.name = attr_name
                column_instance.classes.append('normal_column')
                columns.append((attr_name, column_instance))
        columns.sort(key=lambda x: x[1].creation_counter)

        # Iterate in reverse to preserve final order
        for base in bases[::-1]:
            if hasattr(base, 'base_columns'):
                columns = base.base_columns.items() + columns
        attrs['base_columns'] = datastructures.SortedDict(columns)

        # If the table is in a ResourceBrowser, the column number must meet
        # these limits because of the width of the browser.
        if opts.browser_table == "navigation" and len(columns) > 1:
            raise ValueError("You can only assign one column to %s."
                             % class_name)
        if opts.browser_table == "content" and len(columns) > 2:
            raise ValueError("You can only assign two columns to %s."
                             % class_name)

        if opts.columns:
            # Remove any columns that weren't declared if we're being explicit
            # NOTE: we're iterating a COPY of the list here!
            for column_data in columns[:]:
                if column_data[0] not in opts.columns:
                    columns.pop(columns.index(column_data))
            # Re-order based on declared columns
            columns.sort(key=lambda x: attrs['_meta'].columns.index(x[0]))
        # Add in our auto-generated columns
        if opts.multi_select and opts.browser_table != "navigation":
            multi_select = opts.column_class("multi_select",
                                             verbose_name="",
                                             auto="multi_select")
            multi_select.classes.append('multi_select_column')
            columns.insert(0, ("multi_select", multi_select))
        if opts.actions_column:
            actions_column = opts.column_class("actions",
                                               verbose_name=_("Actions"),
                                               auto="actions")
            actions_column.classes.append('actions_column')
            columns.append(("actions", actions_column))
        # Store this set of columns internally so we can copy them per-instance
        attrs['_columns'] = datastructures.SortedDict(columns)

        # Gather and register actions for later access since we only want
        # to instantiate them once.
        # (list() call gives deterministic sort order, which sets don't have.)
        actions = list(set(opts.row_actions) | set(opts.table_actions))
        actions.sort(key=operator.attrgetter('name'))
        actions_dict = datastructures.SortedDict([(action.name, action())
                                                    for action in actions])
        attrs['base_actions'] = actions_dict
        if opts._filter_action:
            # Replace our filter action with the instantiated version
            opts._filter_action = actions_dict[opts._filter_action.name]

        # Create our new class!
        return type.__new__(mcs, name, bases, attrs)


class DataTable(object):
    """ A class which defines a table with all data and associated actions.

    .. attribute:: name

        String. Read-only access to the name specified in the
        table's Meta options.

    .. attribute:: multi_select

        Boolean. Read-only access to whether or not this table
        should display a column for multi-select checkboxes.

    .. attribute:: data

        Read-only access to the data this table represents.

    .. attribute:: filtered_data

        Read-only access to the data this table represents, filtered by
        the :meth:`~horizon.tables.FilterAction.filter` method of the table's
        :class:`~horizon.tables.FilterAction` class (if one is provided)
        using the current request's query parameters.
    """
    __metaclass__ = DataTableMetaclass

    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        self.request = request
        self.data = data
        self.kwargs = kwargs
        self._needs_form_wrapper = needs_form_wrapper
        self._no_data_message = self._meta.no_data_message
        self.breadcrumb = None
        self.current_item_id = None
        self.permissions = self._meta.permissions

        # Create a new set
        columns = []
        for key, _column in self._columns.items():
            column = copy.copy(_column)
            column.table = self
            columns.append((key, column))
        self.columns = datastructures.SortedDict(columns)
        self._populate_data_cache()

        # Associate these actions with this table
        for action in self.base_actions.values():
            action.table = self

        self.needs_summary_row = any([col.summation
                                      for col in self.columns.values()])

    def __unicode__(self):
        return unicode(self._meta.verbose_name)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._meta.name)

    @property
    def name(self):
        return self._meta.name

    @property
    def footer(self):
        return self._meta.footer

    @property
    def multi_select(self):
        return self._meta.multi_select

    @property
    def filtered_data(self):
        if not hasattr(self, '_filtered_data'):
            self._filtered_data = self.data
            if self._meta.filter and self._meta._filter_action:
                action = self._meta._filter_action
                filter_string = self.get_filter_string()
                request_method = self.request.method
                needs_preloading = (not filter_string
                                    and request_method == 'GET'
                                    and action.needs_preloading)
                valid_method = (request_method == action.method)
                if (filter_string and valid_method) or needs_preloading:
                    if self._meta.mixed_data_type:
                        self._filtered_data = action.data_type_filter(self,
                                                                self.data,
                                                                filter_string)
                    else:
                        self._filtered_data = action.filter(self,
                                                            self.data,
                                                            filter_string)
        return self._filtered_data

    def get_filter_string(self):
        filter_action = self._meta._filter_action
        param_name = filter_action.get_param_name()
        filter_string = self.request.POST.get(param_name, '')
        return filter_string

    def _populate_data_cache(self):
        self._data_cache = {}
        # Set up hash tables to store data points for each column
        for column in self.get_columns():
            self._data_cache[column] = {}

    def _filter_action(self, action, request, datum=None):
        try:
            # Catch user errors in permission functions here
            row_matched = True
            if self._meta.mixed_data_type:
                row_matched = action.data_type_matched(datum)
            return action._allowed(request, datum) and row_matched
        except Exception:
            LOG.exception("Error while checking action permissions.")
            return None

    def is_browser_table(self):
        if self._meta.browser_table:
            return True
        return False

    def render(self):
        """ Renders the table using the template from the table options. """
        table_template = template.loader.get_template(self._meta.template)
        extra_context = {self._meta.context_var_name: self}
        context = template.RequestContext(self.request, extra_context)
        return table_template.render(context)

    def get_absolute_url(self):
        """ Returns the canonical URL for this table.

        This is used for the POST action attribute on the form element
        wrapping the table. In many cases it is also useful for redirecting
        after a successful action on the table.

        For convenience it defaults to the value of
        ``request.get_full_path()`` with any query string stripped off,
        e.g. the path at which the table was requested.
        """
        return self.request.get_full_path().partition('?')[0]

    def get_empty_message(self):
        """ Returns the message to be displayed when there is no data. """
        return self._no_data_message

    def get_object_by_id(self, lookup):
        """
        Returns the data object from the table's dataset which matches
        the ``lookup`` parameter specified. An error will be raised if
        the match is not a single data object.

        We will convert the object id and ``lookup`` to unicode before
        comparison.

        Uses :meth:`~horizon.tables.DataTable.get_object_id` internally.
        """
        if not isinstance(lookup, unicode):
            lookup = unicode(str(lookup), 'utf-8')
        matches = []
        for datum in self.data:
            obj_id = self.get_object_id(datum)
            if not isinstance(obj_id, unicode):
                obj_id = unicode(str(obj_id), 'utf-8')
            if obj_id == lookup:
                matches.append(datum)
        if len(matches) > 1:
            raise ValueError("Multiple matches were returned for that id: %s."
                           % matches)
        if not matches:
            raise exceptions.Http302(self.get_absolute_url(),
                                     _('No match returned for the id "%s".')
                                       % lookup)
        return matches[0]

    @property
    def has_actions(self):
        """
        Boolean. Indicates whether there are any available actions on this
        table.
        """
        if not self.base_actions:
            return False
        return any(self.get_table_actions()) or any(self._meta.row_actions)

    @property
    def needs_form_wrapper(self):
        """
        Boolean. Indicates whather this table should be rendered wrapped in
        a ``<form>`` tag or not.
        """
        # If needs_form_wrapper is explicitly set, defer to that.
        if self._needs_form_wrapper is not None:
            return self._needs_form_wrapper
        # Otherwise calculate whether or not we need a form element.
        return self.has_actions

    def get_table_actions(self):
        """ Returns a list of the action instances for this table. """
        bound_actions = [self.base_actions[action.name] for
                         action in self._meta.table_actions]
        return [action for action in bound_actions if
                self._filter_action(action, self.request)]

    def get_row_actions(self, datum):
        """ Returns a list of the action instances for a specific row. """
        bound_actions = []
        for action in self._meta.row_actions:
            # Copy to allow modifying properties per row
            bound_action = copy.copy(self.base_actions[action.name])
            bound_action.attrs = copy.copy(bound_action.attrs)
            bound_action.datum = datum
            # Remove disallowed actions.
            if not self._filter_action(bound_action,
                                       self.request,
                                       datum):
                continue
            # Hook for modifying actions based on data. No-op by default.
            bound_action.update(self.request, datum)
            # Pre-create the URL for this link with appropriate parameters
            if issubclass(bound_action.__class__, table_actions.LinkAction):
                bound_action.bound_url = bound_action.get_link_url(datum)
            bound_actions.append(bound_action)
        return bound_actions

    def render_table_actions(self):
        """ Renders the actions specified in ``Meta.table_actions``. """
        template_path = self._meta.table_actions_template
        table_actions_template = template.loader.get_template(template_path)
        bound_actions = self.get_table_actions()
        extra_context = {"table_actions": bound_actions}
        if self._meta.filter and \
           self._filter_action(self._meta._filter_action, self.request):
            extra_context["filter"] = self._meta._filter_action
        context = template.RequestContext(self.request, extra_context)
        return table_actions_template.render(context)

    def render_row_actions(self, datum):
        """
        Renders the actions specified in ``Meta.row_actions`` using the
        current row data. """
        template_path = self._meta.row_actions_template
        row_actions_template = template.loader.get_template(template_path)
        bound_actions = self.get_row_actions(datum)
        extra_context = {"row_actions": bound_actions,
                         "row_id": self.get_object_id(datum)}
        context = template.RequestContext(self.request, extra_context)
        return row_actions_template.render(context)

    @staticmethod
    def parse_action(action_string):
        """
        Parses the ``action`` parameter (a string) sent back with the
        POST data. By default this parses a string formatted as
        ``{{ table_name }}__{{ action_name }}__{{ row_id }}`` and returns
        each of the pieces. The ``row_id`` is optional.
        """
        if action_string:
            bits = action_string.split(STRING_SEPARATOR)
            bits.reverse()
            table = bits.pop()
            action = bits.pop()
            try:
                object_id = bits.pop()
            except IndexError:
                object_id = None
            return table, action, object_id

    def take_action(self, action_name, obj_id=None, obj_ids=None):
        """
        Locates the appropriate action and routes the object
        data to it. The action should return an HTTP redirect
        if successful, or a value which evaluates to ``False``
        if unsuccessful.
        """
        # See if we have a list of ids
        obj_ids = obj_ids or self.request.POST.getlist('object_ids')
        action = self.base_actions.get(action_name, None)
        if not action or action.method != self.request.method:
            # We either didn't get an action or we're being hacked. Goodbye.
            return None

        # Meanhile, back in Gotham...
        if not action.requires_input or obj_id or obj_ids:
            if obj_id:
                obj_id = self.sanitize_id(obj_id)
            if obj_ids:
                obj_ids = [self.sanitize_id(i) for i in obj_ids]
            # Single handling is easy
            if not action.handles_multiple:
                response = action.single(self, self.request, obj_id)
            # Otherwise figure out what to pass along
            else:
                # Preference given to a specific id, since that implies
                # the user selected an action for just one row.
                if obj_id:
                    obj_ids = [obj_id]
                response = action.multiple(self, self.request, obj_ids)
            return response
        elif action and action.requires_input and not (obj_id or obj_ids):
            messages.info(self.request,
                          _("Please select a row before taking that action."))
        return None

    @classmethod
    def check_handler(cls, request):
        """ Determine whether the request should be handled by this table. """
        if request.method == "POST" and "action" in request.POST:
            table, action, obj_id = cls.parse_action(request.POST["action"])
        elif "table" in request.GET and "action" in request.GET:
            table = request.GET["table"]
            action = request.GET["action"]
            obj_id = request.GET.get("obj_id", None)
        else:
            table = action = obj_id = None
        return table, action, obj_id

    def maybe_preempt(self):
        """
        Determine whether the request should be handled by a preemptive action
        on this table or by an AJAX row update before loading any data.
        """
        request = self.request
        table_name, action_name, obj_id = self.check_handler(request)

        if table_name == self.name:
            # Handle AJAX row updating.
            new_row = self._meta.row_class(self)
            if new_row.ajax and new_row.ajax_action_name == action_name:
                try:
                    datum = new_row.get_data(request, obj_id)
                    new_row.load_cells(datum)
                    error = False
                except Exception:
                    datum = None
                    error = exceptions.handle(request, ignore=True)
                if request.is_ajax():
                    if not error:
                        return django.http.HttpResponse(new_row.render())
                    else:
                        return django.http.HttpResponse(
                                    status=error.status_code)

            preemptive_actions = [action for action in
                                  self.base_actions.values() if action.preempt]
            if action_name:
                for action in preemptive_actions:
                    if action.name == action_name:
                        handled = self.take_action(action_name, obj_id)
                        if handled:
                            return handled
        return None

    def maybe_handle(self):
        """
        Determine whether the request should be handled by any action on this
        table after data has been loaded.
        """
        request = self.request
        table_name, action_name, obj_id = self.check_handler(request)
        if table_name == self.name and action_name:
            return self.take_action(action_name, obj_id)
        return None

    def sanitize_id(self, obj_id):
        """ Override to modify an incoming obj_id to match existing
        API data types or modify the format.
        """
        return obj_id

    def get_object_id(self, datum):
        """ Returns the identifier for the object this row will represent.

        By default this returns an ``id`` attribute on the given object,
        but this can be overridden to return other values.

        .. warning::

            Make sure that the value returned is a unique value for the id
            otherwise rendering issues can occur.
        """
        return datum.id

    def get_object_display(self, datum):
        """ Returns a display name that identifies this object.

        By default, this returns a ``name`` attribute from the given object,
        but this can be overriden to return other values.
        """
        if hasattr(datum, 'name'):
            return datum.name
        return None

    def has_more_data(self):
        """
        Returns a boolean value indicating whether there is more data
        available to this table from the source (generally an API).

        The method is largely meant for internal use, but if you want to
        override it to provide custom behavior you can do so at your own risk.
        """
        return self._meta.has_more_data

    def get_marker(self):
        """
        Returns the identifier for the last object in the current data set
        for APIs that use marker/limit-based paging.
        """
        return http.urlquote_plus(self.get_object_id(self.data[-1]))

    def get_pagination_string(self):
        """ Returns the query parameter string to paginate this table. """
        return "=".join([self._meta.pagination_param, self.get_marker()])

    def calculate_row_status(self, statuses):
        """
        Returns a boolean value determining the overall row status
        based on the dictionary of column name to status mappings passed in.

        By default, it uses the following logic:

        #. If any statuses are ``False``, return ``False``.
        #. If no statuses are ``False`` but any or ``None``, return ``None``.
        #. If all statuses are ``True``, return ``True``.

        This provides the greatest protection against false positives without
        weighting any particular columns.

        The ``statuses`` parameter is passed in as a dictionary mapping
        column names to their statuses in order to allow this function to
        be overridden in such a way as to weight one column's status over
        another should that behavior be desired.
        """
        values = statuses.values()
        if any([status is False for status in values]):
            return False
        elif any([status is None for status in values]):
            return None
        else:
            return True

    def get_row_status_class(self, status):
        """
        Returns a css class name determined by the status value. This class
        name is used to indicate the status of the rows in the table if
        any ``status_columns`` have been specified.
        """
        if status is True:
            return "status_up"
        elif status is False:
            return "status_down"
        else:
            return "status_unknown"

    def get_columns(self):
        """ Returns this table's columns including auto-generated ones."""
        return self.columns.values()

    def get_rows(self):
        """ Return the row data for this table broken out by columns. """
        rows = []
        try:
            for datum in self.filtered_data:
                row = self._meta.row_class(self, datum)
                if self.get_object_id(datum) == self.current_item_id:
                    self.selected = True
                    row.classes.append('current_selected')
                rows.append(row)
        except Exception:
            # Exceptions can be swallowed at the template level here,
            # re-raising as a TemplateSyntaxError makes them visible.
            LOG.exception("Error while rendering table rows.")
            exc_info = sys.exc_info()
            raise template.TemplateSyntaxError, exc_info[1], exc_info[2]
        return rows
