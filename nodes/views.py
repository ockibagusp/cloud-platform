from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsUser
from nodes.models import Nodes
from nodes.serializers import NodeSerializer
from nodes.forms import NodePublishResetForm


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
    def get_object(pk):
        try:
            return Nodes.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get(self, request, pk, format=None):
        node = self.get_object(pk)
        if request.user != node.user and 0 == node.is_public:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = NodeSerializer(node, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        node = self.get_object(pk)
        if request.user != node.user:
            return Response({
                'detail': 'You can not update another person node.'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = NodeSerializer(node, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        node = self.get_object(pk)
        if request.user != node.user:
            return Response({
                'detail': 'You can not delete another person node.'
            }, status=status.HTTP_403_FORBIDDEN)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NodePublishReset(GenericAPIView):
    """
      Reset node publish per day remaining to publish per day initial value.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)

    @staticmethod
    def get_object(pk):
        try:
            return Nodes.objects.get(pk=pk)
        except Exception:
            raise Http404

    def post(self, request):
        form = NodePublishResetForm(request.data)
        if form.is_valid():
            node = self.get_object(form.cleaned_data.get('id'))
            if request.user != node.user:
                return Response({
                    'detail': 'You can not reset  pubsperdayremain of another person node.'
                }, status=status.HTTP_403_FORBIDDEN)
            elif -1 == node.pubsperdayremain:
                return Response({
                    'detail': 'You only can not reset node with unlimited pubsperday'
                }, status=status.HTTP_400_BAD_REQUEST)
            node.pubsperdayremain = node.pubsperday
            node.save()
            serializer = NodeSerializer(node, context={'request': request})
            return Response(serializer.data)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
