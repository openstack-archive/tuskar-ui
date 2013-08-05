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
import random

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon import workflows

from openstack_dashboard import api

from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.forms import DeleteForm
from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.tabs import ResourceClassDetailTabs
from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.workflows import CreateResourceClass
from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.workflows import DetailUpdateWorkflow
from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.workflows import UpdateFlavorsWorkflow
from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.workflows import UpdateRacksWorkflow
from openstack_dashboard.dashboards.infrastructure. \
    resource_management.resource_classes.workflows import UpdateResourceClass


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
                    api.tuskar.ResourceClass.get(self.request,
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


class DetailUpdateView(UpdateView):
    workflow_class = DetailUpdateWorkflow


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
                resource_class = api.tuskar.\
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


class DetailActionView(forms.ModalFormView):
    template_name = ('infrastructure/resource_management/'
                     'resource_classes/action.html')

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        try:
            action = self.request.GET.get('action')
            if action == "delete":
                form_class = DeleteForm

            return form_class(self.request, **self.get_form_kwargs())
        except:
            exceptions.handle(self.request, _("Unable to build an Action."))

    def get_success_url(self):
        # FIXME this should be set on form level
        return reverse("horizon:infrastructure:resource_management:index")

    def get_context_data(self, **kwargs):
        context = super(DetailActionView, self).get_context_data(**kwargs)
        context['resource_class_id'] = self.kwargs['resource_class_id']
        context['action'] = context['form'].initial.get('action', None)
        context['header'] = context['form'].command.header
        return context

    def get_initial(self):
        try:
            resource_class = api.tuskar.ResourceClass.get(
                self.request, self.kwargs['resource_class_id'])
            action = self.request.GET.get('action')
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve resource class data."))
        return {'resource_class': resource_class,
                'action': action}


def rack_health(request, resource_class_id=None):
    # FIXME replace mock data
    random.seed()
    data = []
    statuses = ["Good", "Warnings", "Disaster"]
    colors = ["rgb(244,244,244)", "rgb(240,170,0)", "rgb(200,0,0)"]

    resource_class = (api.tuskar.
                      ResourceClass.get(request,
                                        resource_class_id))

    for rack in resource_class.list_racks:
        rand_index = random.randint(0, 2)
        percentage = (2 - rand_index) * 50
        color = colors[rand_index]

        tooltip = ("<p>Rack: <strong>{0}</strong></p><p>{1}</p>").format(
            rack.name,
            statuses[rand_index])

        data.append({'tooltip': tooltip,
                     'color': color,
                     'status': statuses[rand_index],
                     'percentage': percentage,
                     'id': rack.id,
                     'name': rack.name,
                     'url': "FIXME url"})

        data.sort(key=lambda x: x['percentage'])

    res = {'data': data}
    return HttpResponse(simplejson.dumps(res),
        mimetype="application/json")
