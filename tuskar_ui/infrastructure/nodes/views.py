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

from horizon import exceptions
import horizon.forms
from horizon import tabs as horizon_tabs

from tuskar_ui import api
from tuskar_ui.infrastructure.nodes import forms
from tuskar_ui.infrastructure.nodes import tabs


class IndexView(horizon_tabs.TabbedTableView):
    tab_group_class = tabs.NodeTabs
    template_name = 'infrastructure/nodes/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        try:
            context['free_nodes'] = len(api.Node.list(self.request,
                                                      associated=False))
        except Exception:
            context['free_nodes'] = 0
            exceptions.handle(self.request,
                              _('Unable to retrieve free nodes.'))
        try:
            context['deployed_nodes'] = len(api.Node.list(self.request,
                                                          associated=True))
        except Exception:
            context['deployed_nodes'] = 0
            exceptions.handle(self.request,
                              _('Unable to retrieve deployed nodes.'))

        context['nodes_total'] = \
            context['free_nodes'] + context['deployed_nodes']

        return context


class RegisterView(horizon.forms.ModalFormView):
    form_class = forms.NodeFormset
    form_prefix = 'register_nodes'
    template_name = 'infrastructure/nodes/register.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:nodes:index')

    def get_data(self):
        return []

    def get_form(self, form_class):
        return form_class(self.request.POST or None,
                          initial=self.get_data(),
                          prefix=self.form_prefix)
