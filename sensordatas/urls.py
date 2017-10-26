from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from sensordatas import views

urlpatterns = [
    url(r'^$', views.SensordatasList.as_view(), name="sensordatas-all"),
    url(r'^(?P<pk>\w+)/$', views.SensordatasDetail.as_view(), name="sensordata-detail"),
    url(r'^user/(?P<user>\w+)/$', views.SensordatasFilterUser.as_view(), name="sensordata-filter-user"),
    url(r'^node/(?P<node>\w+)/$', views.SensordatasFilterNode.as_view(),
        name="sensordata-filter-node"),
    url(r'^node/(?P<node>\w+)/sensor/(?P<sensor>\w+)/$', views.SensordatasFilterNodeSensor.as_view(),
        name="sensordata-filter-node-sensor"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
