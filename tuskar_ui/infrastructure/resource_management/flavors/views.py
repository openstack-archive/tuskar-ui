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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tabs as horizon_tabs

from tuskar_ui import api as tuskar
from tuskar_ui.infrastructure.resource_management.flavors import tabs


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.FlavorDetailTabs
    template_name = ('infrastructure/resource_management/flavors/detail.html')

    def get_context_data(self, **kwargs):
            context = super(DetailView, self).get_context_data(**kwargs)
            context["flavor"] = self.get_flavor_data()
            context["resource_class"] = self.get_resource_class_data()
            return context

    def get_flavor_data(self):
        if not hasattr(self, "_flavor"):
            try:
                flavor_id = self.kwargs['flavor_id']
                resource_class_id = self.kwargs['resource_class_id']
                flavor = tuskar.Flavor.get(
                    self.request, resource_class_id, flavor_id)
            except Exception:
                redirect = urlresolvers.reverse(
                    'horizon:infrastructure:resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'flavor "%s".') % flavor_id,
                                  redirect=redirect)
            self._flavor = flavor
        return self._flavor

    def get_resource_class_data(self):
        if not hasattr(self, "_resource_class"):
            try:
                resource_class_id = self.kwargs['resource_class_id']
                resource_class = tuskar.ResourceClass.get(self.request,
                                                          resource_class_id)
            except Exception:
                redirect = urlresolvers.reverse(
                    'horizon:infrastructure:resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for resource '
                                    'class "%s".') % resource_class_id,
                                  redirect=redirect)
            self._resource_class = resource_class
        return self._resource_class

    def get_tabs(self, request, *args, **kwargs):
        flavor = self.get_flavor_data()
        resource_class = self.get_resource_class_data()
        return self.tab_group_class(request,
                                    flavor=flavor,
                                    resource_class=resource_class,
                                    **kwargs)
