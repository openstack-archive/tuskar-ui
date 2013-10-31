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

"""
Views for managing resource classes
"""
import logging
import random

from django.core import urlresolvers
import django.http
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs

from tuskar_ui import api as tuskar

from tuskar_ui.infrastructure.resource_management.resource_classes import forms
from tuskar_ui.infrastructure.resource_management.resource_classes import tabs
from tuskar_ui.infrastructure.resource_management.resource_classes\
    import workflows
from tuskar_ui import workflows as tuskar_workflows


LOG = logging.getLogger(__name__)


class CreateView(tuskar_workflows.WorkflowView):
    workflow_class = workflows.CreateResourceClass

    def get_initial(self):
        pass


class UpdateView(tuskar_workflows.WorkflowView):
    workflow_class = workflows.UpdateResourceClass

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["resource_class_id"] = self.kwargs['resource_class_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            resource_class_id = self.kwargs['resource_class_id']
            try:
                self._object = \
                    tuskar.ResourceClass.get(self.request,
                                             resource_class_id)
            except Exception:
                redirect = urlresolvers.reverse('horizon:infrastructure:'
                                                'resource_management:index')
                msg = _('Unable to retrieve resource class details.')
                exceptions.handle(self.request, msg, redirect=redirect)

        return self._object

    def get_initial(self):
        resource_class = self._get_object()

        return {
            'resource_class_id': resource_class.id,
            'name': resource_class.name,
            'service_type': resource_class.service_type,
            'image_id': resource_class.image_id,
        }


class DetailUpdateView(UpdateView):
    workflow_class = workflows.DetailUpdateWorkflow


class UpdateRacksView(UpdateView):
    workflow_class = workflows.UpdateRacksWorkflow


class UpdateFlavorsView(UpdateView):
    workflow_class = workflows.UpdateFlavorsWorkflow


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.ResourceClassDetailTabs
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
                resource_class = tuskar.ResourceClass.get(self.request,
                                                          resource_class_id)
            except Exception:
                redirect = urlresolvers.reverse('horizon:infrastructure:'
                                                'resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'resource class "%s".')
                                  % resource_class_id, redirect=redirect)
            self._resource_class = resource_class
        return self._resource_class

    def get_tabs(self, request, *args, **kwargs):
        resource_class = self.get_data()
        return self.tab_group_class(request, resource_class=resource_class,
                                    **kwargs)


class DetailActionView(horizon_forms.ModalFormView):
    template_name = ('infrastructure/resource_management/'
                     'resource_classes/action.html')

    def get_form(self, form_class):
        """Returns an instance of the form to be used in this view."""
        try:
            action = self.request.GET.get('action')
            if action == "delete":
                form_class = forms.DeleteForm

            return form_class(self.request, **self.get_form_kwargs())
        except Exception:
            exceptions.handle(self.request, _("Unable to build an Action."))

    def get_success_url(self):
        # FIXME this should be set on form level
        return urlresolvers.reverse('horizon:infrastructure:'
                                    'resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(DetailActionView, self).get_context_data(**kwargs)
        context['resource_class_id'] = self.kwargs['resource_class_id']
        context['action'] = context['form'].initial.get('action', None)
        context['header'] = context['form'].command.header
        return context

    def get_initial(self):
        try:
            resource_class = tuskar.ResourceClass.get(
                self.request, self.kwargs['resource_class_id'])
            action = self.request.GET.get('action')
        except Exception:
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

    resource_class = (tuskar.ResourceClass.get(request,
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
    return django.http.HttpResponse(simplejson.dumps(res),
                                    mimetype="application/json")
