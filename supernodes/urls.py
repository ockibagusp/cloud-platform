from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from supernodes import views as node_views

urlpatterns = [
    url(r'^$', node_views.SuperNodesList.as_view(), name="supernodes-all"),
    url(r'^(?P<pk>\w+)/$', node_views.SupernodeDetail.as_view(), name="supernodes-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)