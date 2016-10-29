from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from nodes.models import Nodes
from nodes.serializers import NodeSerializer
from sensors.serializers import SensorSerializer


class NodesList(ListAPIView):
    queryset = Nodes.objects.all()
    serializer_class = NodeSerializer


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
