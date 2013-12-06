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
from django.views import generic
from django.core.urlresolvers import reverse_lazy  # noqa
import horizon.forms

from tuskar_ui.infrastructure.deploy_overview import forms


class IndexView(generic.TemplateView):
    template_name = 'infrastructure/deploy_overview/index.html'


class RegisterView(horizon.forms.ModalFormView):
    form_class = forms.RegisterNodesForm
    template_name = 'infrastructure/deploy_overview/register.html'
    success_url = reverse_lazy("horizon:infrastructure:deploy_overview:index")

    def get_data(self):
        return [
            {'name': 'Node 1'},
            {'name': 'Node 2'},
        ]

    def get_context_data(self, *args, **kwargs):
        context = super(RegisterView, self).get_context_data(*args, **kwargs)
        context['formset'] = forms.NodeFormset(self.request.POST or None,
                                               initial=self.get_data(),
                                               prefix='register_nodes')
        context['ziew'] = 'ziew'
        return context
