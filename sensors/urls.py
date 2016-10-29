from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from sensors import views

urlpatterns = [
    url(r'^$', views.SensorsList.as_view(), name="sensors-all"),
    url(r'^(?P<pk>[0-9]+)/$', views.SensorDetail.as_view(), name="sensors-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
