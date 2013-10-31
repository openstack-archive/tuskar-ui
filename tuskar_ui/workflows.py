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

import logging

from django import template
from django.utils import datastructures

import horizon.workflows


LOG = logging.getLogger(__name__)


# A WorkflowView that uses tuskar's base template with additional CSS and JS
class WorkflowView(horizon.workflows.WorkflowView):
    template_name = 'infrastructure/_workflow_base.html'


# FIXME: TableStep
class TableStep(horizon.workflows.Step):
    """A :class:`~horizon.workflows.Step` class which knows how to deal with
    :class:`~horizon.tables.DataTable` classes rendered inside of it.

    This distinct class is required due to the complexity involved in handling
    both dynamic tab loading, dynamic table updating and table actions all
    within one view.

    .. attribute:: table_classes

        An iterable containing the :class:`~horizon.tables.DataTable` classes
        which this tab will contain. Equivalent to the
        :attr:`~horizon.tables.MultiTableView.table_classes` attribute on
        :class:`~horizon.tables.MultiTableView`. For each table class you
        need to define a corresponding ``get_{{ table_name }}_data`` method
        as with :class:`~horizon.tables.MultiTableView`.
    """

    table_classes = None

    def __init__(self, workflow):
        super(TableStep, self).__init__(workflow)
        if not self.table_classes:
            class_name = self.__class__.__name__
            raise NotImplementedError("You must define a table_class "
                                      "attribute on %s" % class_name)
        # Instantiate our table classes but don't assign data yet
        table_instances = [(table._meta.name,
                            table(workflow.request, needs_form_wrapper=False))
                           for table in self.table_classes]
        self._tables = datastructures.SortedDict(table_instances)
        self._table_data_loaded = False

    def prepare_action_context(self, request, context):
        """Passes the tables to the action for validation and data extraction.
        """
        self.load_table_data()
        context['_tables'] = self._tables
        return context

    def render(self):
        """Renders the step."""
        step_template = template.loader.get_template(self.template_name)
        extra_context = {"form": self.action,
                         "step": self}

        # FIXME: TableStep:
        if issubclass(self.__class__, TableStep):
            extra_context.update(self.get_context_data(self.workflow.request))

        context = template.RequestContext(self.workflow.request, extra_context)
        return step_template.render(context)

    def load_table_data(self):
        """Calls the ``get_{{ table_name }}_data`` methods for each table class
        and sets the data on the tables.
        """
        # We only want the data to be loaded once, so we track if we have...
        if not self._table_data_loaded:
            for table_name, table in self._tables.items():
                # Fetch the data function.
                func_name = "get_%s_data" % table_name
                data_func = getattr(self, func_name, None)
                if data_func is None:
                    cls_name = self.__class__.__name__
                    raise NotImplementedError("You must define a %s method "
                                              "on %s." % (func_name, cls_name))
                # Load the data.
                table.data = data_func()
                table._meta.has_more_data = self.has_more_data(table)
            # Mark our data as loaded so we don't run the loaders again.
            self._table_data_loaded = True

    def get_context_data(self, request):
        """Adds a ``{{ table_name }}_table`` item to the context for each table
        in the :attr:`~horizon.tabs.TableTab.table_classes` attribute.

        If only one table class is provided, a shortcut ``table`` context
        variable is also added containing the single table.
        """
        context = {}
        # If the data hasn't been manually loaded before now,
        # make certain it's loaded before setting the context.
        self.load_table_data()
        for table_name, table in self._tables.items():
            # If there's only one table class, add a shortcut name as well.
            if len(self.table_classes) == 1:
                context["table"] = table
            context["%s_table" % table_name] = table
        return context

    def has_more_data(self, table):
        return False
