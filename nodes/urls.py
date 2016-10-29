from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from nodes import views

urlpatterns = [
    url(r'^$', views.NodesList.as_view(), name="nodes-all"),
    url(r'^(?P<pk>[0-9]+)/$', views.NodeDetail.as_view(), name="nodes-detail"),
    url(r'^(?P<pk>[0-9]+)/sensor/$', views.NodeSensorList.as_view(), name="node-sensor-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
