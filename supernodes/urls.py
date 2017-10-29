from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from supernodes import views as supernode_views
from nodes import views as node_views

urlpatterns = [
    url(r'^$', supernode_views.SuperNodesList.as_view(), name="supernodes-all"),
    url(r'^(?P<pk>\w+)/$', supernode_views.SupernodeDetail.as_view(), name="supernodes-detail"),
    url(r'^(?P<pk>\w+)/nodes/$', node_views.NodesList.as_view(), name="supernodes-node-list")
]

urlpatterns = format_suffix_patterns(urlpatterns)