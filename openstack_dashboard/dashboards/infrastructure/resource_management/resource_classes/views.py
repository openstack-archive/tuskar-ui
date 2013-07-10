# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""
Views for managing resource classes
"""
import logging

from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from horizon import tabs
from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api

from .workflows import (CreateResourceClass, UpdateResourceClass,
                        UpdateRacksWorkflow, UpdateFlavorsWorkflow)
from .tables import ResourceClassesTable
from .tabs import ResourceClassDetailTabs

LOG = logging.getLogger(__name__)


class CreateView(workflows.WorkflowView):
    workflow_class = CreateResourceClass

    def get_initial(self):
        pass


class UpdateView(workflows.WorkflowView):
    workflow_class = UpdateResourceClass

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["resource_class_id"] = self.kwargs['resource_class_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            resource_class_id = self.kwargs['resource_class_id']
            try:
                self._object = \
                    api.management.ResourceClass.get(self.request,
                                                     resource_class_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve resource class details.')
                exceptions.handle(self.request, msg, redirect=redirect)

        return self._object

    def get_initial(self):
        resource_class = self._get_object()

        return {'resource_class_id': resource_class.id,
                'name': resource_class.name,
                'service_type': resource_class.service_type}


class UpdateRacksView(UpdateView):
    workflow_class = UpdateRacksWorkflow


class UpdateFlavorsView(UpdateView):
    workflow_class = UpdateFlavorsWorkflow


class DetailView(tabs.TabView):
    tab_group_class = ResourceClassDetailTabs
    template_name = ('infrastructure/resource_management/resource_classes/'
                     'detail.html')

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["resource_class"] = self.get_data()
        return context

    def get_data(self):
        if not hasattr(self, "_resource_class"):
            try:
                resource_class_id = self.kwargs['resource_class_id']
                resource_class = api.management.\
                                     ResourceClass.get(self.request,
                                                       resource_class_id)
            except:
                redirect = reverse('horizon:infrastructure:'
                                   'resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'resource class "%s".')
                                    % resource_class_id,
                                    redirect=redirect)
            self._resource_class = resource_class
        return self._resource_class

    def get_tabs(self, request, *args, **kwargs):
        resource_class = self.get_data()
        return self.tab_group_class(request, resource_class=resource_class,
                                    **kwargs)
