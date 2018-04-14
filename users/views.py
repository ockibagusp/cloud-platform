from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsAdmin
from cloud_platform.helpers import is_objectid_valid
from users.models import User
from users.serializers import UserSerializer


class UsersList(ListAPIView):
    """
    Retrieve  Users instance.
    There are 2 types of user: Admin and Researcher.

    Usage:
    /                   => retrieve both admin and researcher users
    /?type=admin        => retrieve admin users
    /?type=researcher   => retrieve researcher users

    NB:
    incorrect type params will return empty data.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer

    @staticmethod
    def get_users(role=None):
        if not role:
            return User.objects.all()
        else:
            if 'admin' == role:
                return User.objects.filter(is_admin=1)
            elif 'researcher' == role:
                return User.objects.filter(is_admin=0)
            else:
                return []

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_users(request.GET.get('type')))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(GenericAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdmin,)

    @staticmethod
    def get_user(pk):
        try:
            return User.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get(self, request, pk):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_user(pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_user(pk)
        # ensure that super admin only edited by him/his self
        if "webmaster" == user.username:
            return Response({
                'detail': 'You can not update super admin user data.'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_user(pk)
        # super admin can not be deleted
        if "webmaster" == user.username:
            return Response({
                'detail': 'Super admin can not be deleted.'
            }, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResearcherRegistration(GenericAPIView):
    serializer_class = UserSerializer

    @staticmethod
    def post(request):
        # ensure that new user has role researcher, they can't override this field.
        request.data.update({'is_admin': 0})
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
