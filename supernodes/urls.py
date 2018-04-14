from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from supernodes import views as supernode_views
from nodes import views as node_views
from sensors import views as sensor_views

urlpatterns = [
    url(r'^$', supernode_views.SuperNodesList.as_view(), name="supernodes-all"),
    url(r'^(?P<pk>\w+)/$', supernode_views.SupernodeDetail.as_view(), name="supernodes-detail"),
    url(r'^(?P<pk>\w+)/nodes/$', node_views.NodesList.as_view(), name="supernodes-node-list"),
    url(r'^(?P<pk>\w+)/sensors/$', sensor_views.SupernodeSensorsList.as_view(), name="supernodes-sensors-list"),
    url(r'^(?P<pk>\w+)/sensors/(?P<sensorid>\w+)/$', sensor_views.SupernodeSensorDetail.as_view(), name="supernodes-sensors-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
