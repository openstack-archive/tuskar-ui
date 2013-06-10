from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import tabs
from horizon import exceptions

from openstack_dashboard import api

from .tabs import ResourceClassDetailTabs


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
                                     resource_class_get(self.request,
                                                        resource_class_id)
            except:
                redirect = reverse('horizon:infrastructure:'
                                   'resource_management:resource_classes:'
                                   'index')
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
