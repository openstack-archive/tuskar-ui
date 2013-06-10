from django.utils.translation import ugettext_lazy as _

from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("infrastructure/resource_management/resource_classes/"
                    "_detail_overview.html")
    preload = False

    def get_context_data(self, request):
        return {"resource_class": self.tab_group.kwargs['resource_class']}


class ResourcesTab(tabs.Tab):
    name = _("Resources")
    slug = "resources"
    template_name = ("infrastructure/resource_management/resource_classes/"
                     "_detail_resources.html")
    preload = False

    def get_context_data(self, request):
        pass


class FlavorsTab(tabs.Tab):
    name = _("Flavors")
    slug = "flavors"
    template_name = ("infrastructure/resource_management/resource_classes/"
                     "_detail_flavors.html")
    preload = False

    def get_context_data(self, request):
        pass


class ResourceClassDetailTabs(tabs.TabGroup):
    slug = "resource_class_details"
    tabs = (OverviewTab, ResourcesTab, FlavorsTab)
    sticky = True
