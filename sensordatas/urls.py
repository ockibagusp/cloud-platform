from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from sensordatas import views

urlpatterns = [
    url(r'^(?P<pk>\w+)/$', views.SensordatasDetail.as_view(), name="sensordata-detail"),
    url(r'^user/(?P<user>\w+)/$', views.SensordatasFilterUser.as_view(), name="sensordata-filter-user"),
    url(r'^supernode/(?P<supernode>\w+)/$', views.SensordatasFilterSupernode.as_view(),
        name="sensordata-filter-supernode"),
    url(r'^supernode/(?P<supernode>\w+)/sensor/(?P<sensor>\w+)/$',
        views.SensordatasFilterSupernodeSensor.as_view(),name="sensordata-filter-supernode-sensor"),
    url(r'^node/(?P<node>\w+)/$', views.SensordatasFilterNode.as_view(),
        name="sensordata-filter-node"),
    url(r'^node/(?P<node>\w+)/sensor/(?P<sensor>\w+)/$', views.SensordatasFilterNodeSensor.as_view(),
        name="sensordata-filter-node-sensor"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
