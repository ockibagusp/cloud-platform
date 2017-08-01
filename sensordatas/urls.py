from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from sensordatas import views

urlpatterns = [
    url(r'^$', views.SubscriptionsList.as_view(), name="sensordatas-all"),
    url(r'^(?P<pk>\w+)/$', views.SubscriptionDetail.as_view(), name="sensordata-detail"),
    url(r'^user/(?P<user>\w+)/$', views.SubscriptionFilterUser1.as_view(), name="sensordata-filter-user"),
    url(r'^user0/(?P<user>\w+)/$', views.SubscriptionFilterUser0.as_view(), name="sensordata-filter-user2"),
    url(r'^node/(?P<node>\w+)/$', views.SubscriptionFilterNode.as_view(),
        name="sensordata-filter-node"),
    url(r'^node/(?P<node>\w+)/sensor/(?P<sensor>\w+)/$', views.SubscriptionFilterNodeSensor.as_view(),
        name="sensordata-filter-node-sensor"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
