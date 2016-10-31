from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from nodes.models import Nodes
from nodes.serializers import NodeSerializer
from sensors.serializers import SensorSerializer


class NodesList(ListAPIView):
    queryset = Nodes.objects.all()
    serializer_class = NodeSerializer

    @staticmethod
    def post(request):
        serializer = NodeSerializer(data=request.data, context={'request': request},)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeDetail(APIView):
    """
    Retrieve, update or delete a Nodes instance.
    """

    @staticmethod
    def get_object(pk):
        try:
            return Nodes.objects.get(pk=pk)
        except Nodes.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        node = self.get_object(pk)
        serializer = NodeSerializer(node, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
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


class NodeSensorList(APIView):
    """
    Retrieve Sensors instance with specific Nodes.
    """

    @staticmethod
    def get_object(pk):
        try:
            return Nodes.objects.get(pk=pk)
        except Nodes.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        node = self.get_object(pk)
        serializer = SensorSerializer(node.sensors_set, context={'request': request}, many=True)
        return Response(serializer.data)
