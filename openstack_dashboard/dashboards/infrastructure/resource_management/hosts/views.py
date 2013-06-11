# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api

from .tabs import HostDetailTabs


class DetailView(tabs.TabView):
    tab_group_class = HostDetailTabs
    template_name = 'infrastructure/resource_management/hosts/detail.html'

    def get_context_data(self, **kwargs):
            context = super(DetailView, self).get_context_data(**kwargs)
            context["host"] = self.get_data()
            return context

    def get_data(self):
        if not hasattr(self, "_host"):
            try:
                host_id = self.kwargs['host_id']
                host = api.management.Host.get(self.request, host_id)
            except:
                redirect = reverse('horizon:infrastructure:'
                                   'resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'host "%s".')
                                    % host_id,
                                    redirect=redirect)
            self._host = host
        return self._host

    def get_tabs(self, request, *args, **kwargs):
        host = self.get_data()
        return self.tab_group_class(request, host=host,
                                    **kwargs)
