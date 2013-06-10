from django.conf.urls.defaults import patterns, url

from .views import DetailView


urlpatterns = patterns('',
    url(r'^(?P<resource_class_id>[^/]+)/$',
        DetailView.as_view(), name='detail'),
)
