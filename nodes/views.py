from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsUser
from nodes.models import Nodes
from nodes.serializers import NodeSerializer
from users.models import User


class NodesList(ListAPIView):
    """
    Retrieve  Nodes instance.
    Every nodes has visibility option: public and private.

    Usage:
    /               => retrieve all authenticated user nodes
    /?role=public   => retrieve authenticated user public nodes
    /?role=private  => retrieve authenticated user private nodes
    /?role=global   => retrieve all public nodes from other users
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = NodeSerializer

    @staticmethod
    def get_nodes(user, role=None):
        if not role:
            return Nodes.objects.filter(user=user)
        else:
            if 'global' == role:
                return Nodes.objects.filter(user__ne=user, is_public=1)
            elif 'public' == role:
                return Nodes.objects.filter(user=user, is_public=1)
            else:  # private
                return Nodes.objects.filter(user=user, is_public=0)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_nodes(request.user, request.GET.get('role')))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NodeSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        request.data.update({'user': request.user.username})
        serializer = NodeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeDetail(GenericAPIView):
    """
    Retrieve, update or delete a Nodes instance.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)

    @staticmethod
    def check_user(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return False

    @staticmethod
    def get_object(pk):
        try:
            return Nodes.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get(self, request, pk, format=None):
        node = self.get_object(pk)
        serializer = NodeSerializer(node, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = request.data.get('user')
        if not self.check_user(user):
            return Response({
                'user': 'User with username=%s does not exist.' % user
            }, status=status.HTTP_400_BAD_REQUEST)

        node = self.get_object(pk)
        serializer = NodeSerializer(node, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        node = self.get_object(pk)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
