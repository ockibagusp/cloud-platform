from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsUser
from cloud_platform.helpers import is_objectid_valid

from supernodes.models import Supernodes
from supernodes.serializers import SuperNodesSerializer


class SuperNodesList(ListAPIView):
    """
    Retrieve  SuperNodes instance.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = SuperNodesSerializer

    @staticmethod
    def get_supernodes(user):
        return Supernodes.objects.filter(user=user)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_supernodes(request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SuperNodesSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        from django.http import QueryDict
        if isinstance(request.data, QueryDict):
            return Response({
                'detail': 'Payload cannot be empty.'
            }, status=status.HTTP_400_BAD_REQUEST)
        # SlugRelatedField, avoid 'query does not matching' exception on non valid data payload
        if request.data.get('user'):
            request.data.pop('user')
        request.data.update({'user': request.user.username})
        serializer = SuperNodesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupernodeDetail(GenericAPIView):
    """
    Retrieve, update or delete a Nodes instance.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)

    @staticmethod
    def get_object(pk):
        try:
            return Supernodes.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get(self, request, pk, format=None):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        supernode = self.get_object(pk)
        if request.user != supernode.user:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = SuperNodesSerializer(supernode, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        supernode = self.get_object(pk)
        if request.user != supernode.user:
            return Response({
                'detail': 'You can not update another person supernode.'
            }, status=status.HTTP_403_FORBIDDEN)
        # SlugRelatedField, avoid 'query does not matching' exception on non valid data payload
        if request.data.get('user'):
            request.data.pop('user')
        serializer = SuperNodesSerializer(supernode, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        supernode = self.get_object(pk)
        if request.user != supernode.user:
            return Response({
                'detail': 'You can not delete another person supernode.'
            }, status=status.HTTP_403_FORBIDDEN)
        supernode.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
