from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from subscriptions import views

urlpatterns = [
    url(r'^$', views.SubscriptionsList.as_view(), name="subscriptions-all"),
    url(r'^(?P<pk>\w+)/$', views.SubscriptionDetail.as_view(), name="subscription-detail"),
    url(r'^user/(?P<user>\w+)/$', views.SubscriptionFilterUser.as_view(), name="subscription-filter-user"),
    url(r'^node/(?P<node>\w+)/$', views.SubscriptionFilterNode.as_view(),
        name="subscription-filter-node"),
    url(r'^node/(?P<node>\w+)/sensor/(?P<sensor>\w+)/$', views.SubscriptionFilterNodeSensor.as_view(),
        name="subscription-filter-node-sensor"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
