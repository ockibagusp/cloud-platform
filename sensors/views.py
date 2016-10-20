from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from sensors.models import Sensors
from sensors.serializers import SensorSerializer


class SensorsList(APIView):
    @staticmethod
    def get(request, format=None):
        sensors = Sensors.objects.all()
        serializer = SensorSerializer(sensors, many=True, context={'request': request})
        return Response(serializer.data)


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
