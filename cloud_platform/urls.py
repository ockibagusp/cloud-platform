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
from rest_framework.decorators import api_view
from rest_framework.response import Response

from authenticate.views import SupernodeTokenCreator, UserTokenCreator
from users.views import ResearcherRegistration


@api_view(['GET'])
def welcome(request):
    return Response({"message": "Welcome to AgriHub API!"})


urlpatterns = [
    url(r'^$', welcome),
    url(r'^users/', include('users.urls')),
    url(r'^supernodes/', include('supernodes.urls')),
    url(r'^nodes/', include('nodes.urls')),
    url(r'^sensordatas/', include('sensordatas.urls')),
    url(r'^user-auth/', UserTokenCreator.as_view()),
    url(r'^supernode-auth/$', SupernodeTokenCreator.as_view()),
    url(r'^register/$', ResearcherRegistration.as_view())
]
