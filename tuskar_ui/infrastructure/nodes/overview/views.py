# -*- coding: utf8 -*-
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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from horizon import exceptions
import horizon.forms

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms


class IndexView(generic.TemplateView):
    template_name = 'infrastructure/nodes.overview/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            free_nodes = len(api.Node.list(self.request, associated=False))
        except Exception:
            free_nodes = 0
            exceptions.handle(self.request,
                              _('Unable to retrieve free nodes.'))
        try:
            allocated_nodes = len(api.Node.list(self.request, associated=True))
        except Exception:
            allocated_nodes = 0
            exceptions.handle(self.request,
                              _('Unable to retrieve allocated nodes.'))
        context.update({
            'nodes_total': free_nodes + allocated_nodes,
            'nodes_allocated_resources': allocated_nodes,
            'nodes_unallocated': free_nodes,
        })
        return context


class RegisterView(horizon.forms.ModalFormView):
    form_class = forms.NodeFormset
    form_prefix = 'register_nodes'
    template_name = 'infrastructure/nodes.overview/register.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:nodes.overview:index')

    def get_data(self):
        return []

    def get_form(self, form_class):
        return form_class(self.request.POST or None,
                          initial=self.get_data(),
                          prefix=self.form_prefix)
