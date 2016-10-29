from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from sensors.models import Sensors
from sensors.serializers import SensorSerializer


class SensorsList(ListAPIView):
    queryset = Sensors.objects.all()
    serializer_class = SensorSerializer


class SensorDetail(APIView):
    """
    Retrieve, update or delete a Sensor instance.
    """

    @staticmethod
    def get_object(pk):
        try:
            return Sensors.objects.get(pk=pk)
        except Sensors.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        node = self.get_object(pk)
        serializer = SensorSerializer(node, context={'request': request})
        return Response(serializer.data)
