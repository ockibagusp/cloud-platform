from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from subscriptions import views

urlpatterns = [
    url(r'^$', views.SubscriptionsList.as_view(), name="subscriptions-all"),
    url(r'^(?P<pk>[0-9]+)/$', views.SubscriptionDetail.as_view(), name="subscription-detail"),
    url(r'^(?P<user>\w+)/$', views.SubscriptionFilterUser.as_view(), name="subscription-filter-user"),
    url(r'^(?P<node>\w+)/(?P<sensor>\w+)$', views.SubscriptionFilter.as_view(), name="subscription-filter"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
