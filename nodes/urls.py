from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from nodes import views as node_views
from sensors import views as sensor_views

urlpatterns = [
    url(r'^$', node_views.NodesList.as_view(), name="nodes-all"),
    url(r'^reset/$', node_views.NodePublishReset.as_view(), name="nodes-reset"),
    url(r'^duplicate/$', node_views.NodeDuplicate.as_view(), name="nodes-duplicate"),
    url(r'^(?P<pk>\w+)/$', node_views.NodeDetail.as_view(), name="nodes-detail"),
    url(r'^(?P<pk>\w+)/sensor/$', sensor_views.SensorsList.as_view(), name="node-sensors-list"),
    url(r'^(?P<pk>\w+)/sensor/(?P<sensorid>\w+)/$', sensor_views.SensorDetail.as_view(), name="node-sensor-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
