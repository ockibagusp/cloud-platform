"""cloud_gateway URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token

from authenticate.views import TokenCreator

urlpatterns = [
    url(r'^admin-rahasia/', admin.site.urls),
    url(r'^nodes/', include('nodes.urls')),
    url(r'^sensors/', include('sensors.urls')),
    url(r'^subscriptions/', include('subscriptions.urls')),
    url(r'^api-auth/', obtain_jwt_token),
    url(r'^node-auth/$', TokenCreator.as_view()),
]
