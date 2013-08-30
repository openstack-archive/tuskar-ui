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

import datetime
import json
import logging

from django.core.serializers import json as json_serializers
from django.core import urlresolvers
from django import http
from django.utils.translation import ugettext_lazy as _  # noqa
from django.views import generic

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tabs as horizon_tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management.flavor_templates import forms
from tuskar_ui.infrastructure.resource_management.flavor_templates import tabs


LOG = logging.getLogger(__name__)


class CreateView(horizon_forms.ModalFormView):
    form_class = forms.CreateFlavorTemplate
    template_name = ('infrastructure/resource_management/'
                     'flavor_templates/create.html')
    success_url = urlresolvers.reverse_lazy(
        'horizon:infrastructure:resource_management:index')


class EditView(horizon_forms.ModalFormView):
    form_class = forms.EditFlavorTemplate
    template_name = ('infrastructure/resource_management/'
                     'flavor_templates/edit.html')
    form_url = ('horizon:infrastructure:resource_management:'
                'flavor_templates:edit')
    success_url = urlresolvers.reverse_lazy(
        'horizon:infrastructure:resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        context['flavor_template_id'] = self.kwargs['flavor_template_id']
        context['form_url'] = self.form_url
        context['success_url'] = self.get_success_url()
        return context

    def get_initial(self):
        try:
            flavor_template = tuskar.FlavorTemplate.get(
                self.request, self.kwargs['flavor_template_id'])
        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve flavor template data."))
        return {'flavor_template_id': flavor_template.id,
                'name': flavor_template.name,
                'cpu': flavor_template.cpu.value,
                'memory': flavor_template.memory.value,
                'storage': flavor_template.storage.value,
                'ephemeral_disk': flavor_template.ephemeral_disk.value,
                'swap_disk': flavor_template.swap_disk.value}


class DetailEditView(EditView):
    form_url = ('horizon:infrastructure:resource_management:'
                'flavor_templates:detail_edit')
    success_url = ('horizon:infrastructure:resource_management:'
                   'flavor_templates:detail')

    def get_success_url(self):
        return urlresolvers.reverse(
            self.success_url, args=(self.kwargs['flavor_template_id'],))


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.FlavorTemplateDetailTabs
    template_name = ('infrastructure/resource_management/'
                     'flavor_templates/detail.html')

    def get_context_data(self, **kwargs):
            context = super(DetailView, self).get_context_data(**kwargs)
            context["flavor_template"] = self.get_data()
            return context

    def get_data(self):
        if not hasattr(self, "_flavor_template"):
            try:
                flavor_template_id = self.kwargs['flavor_template_id']
                flavor_template = tuskar.FlavorTemplate.get(self.request,
                                                            flavor_template_id)
            except Exception:
                redirect = urlresolvers.reverse(
                    'horizon:infrastructure:resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'flavor template "%s".')
                                    % flavor_template_id,
                                    redirect=redirect)
            self._flavor_template = flavor_template
        return self._flavor_template

    def get_tabs(self, request, *args, **kwargs):
        flavor_template = self.get_data()
        return self.tab_group_class(request, flavor_template=flavor_template,
                                    **kwargs)


class ActiveInstancesDataView(generic.View):

    def get(self, request, *args, **kwargs):
        try:
            flavor_template = tuskar.FlavorTemplate.get(
                self.request, self.kwargs['flavor_template_id'])
            values = flavor_template.vms_over_time(
                datetime.datetime.now() - datetime.timedelta(days=7),
                datetime.datetime.now())
            return http.HttpResponse(
                json.dumps(values, cls=json_serializers.DjangoJSONEncoder),
                mimetype='application/json')
        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve flavor template data."))
