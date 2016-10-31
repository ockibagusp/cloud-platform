from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from sensors.models import Sensors
from sensors.serializers import SensorSerializer


class SensorsList(ListAPIView):
    queryset = Sensors.objects.all()
    serializer_class = SensorSerializer

    @staticmethod
    def post(request):
        serializer = SensorSerializer(data=request.data, context={'request': request}, )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def put(self, request, pk, format=None):
        sensor = self.get_object(pk)
        serializer = SensorSerializer(sensor, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        sensor = self.get_object(pk)
        sensor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)