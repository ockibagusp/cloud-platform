from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from nodes.models import Nodes
from sensors.models import Sensors
from sensors.serializers import SensorSerializer


class SensorsList(ListAPIView):
    serializer_class = SensorSerializer

    @staticmethod
    def get_object(pk):
        try:
            return Nodes.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get_queryset(self):
        node = self.get_object(self.kwargs.get('pk'))
        return node.sensors

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SensorSerializer(page, many=True, context={
                'request': request, 'nodeid': kwargs.get('pk')
            })
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request, pk):
        # TODO batasi julmah sensor dalam satu node
        serializer = SensorSerializer(data=request.data, context={
            'request': request, 'nodeid': pk
        })

        if serializer.is_valid():
            Nodes.objects(pk=pk).update_one(
                push__sensors=Sensors(label=serializer.data.get('label'))
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SensorDetail(GenericAPIView):
    """
    Retrieve, update or delete a Sensor instance.
    """

    @staticmethod
    def get_node(node_pk, sensor_id):
        try:
            node = Nodes.objects.get(pk=node_pk)
            sensor = node.sensors.get(id=sensor_id)
            return {
                'node': node,
                'sensor': sensor
            }
        except Exception:
            raise Http404

    def get(self, request, pk, sensorid):
        data = self.get_node(pk, sensorid)
        serializer = SensorSerializer(data.get('sensor'), context={'request': request, 'nodeid': pk})
        return Response(serializer.data)

    def put(self, request, pk, sensorid):
        """
        Manual validation
        cause any selializer cannot handle EmbededDocummentList update
        """
        data = self.get_node(pk, sensorid)
        node = data.get('node')
        tmp_sensors = data.get('node').sensors

        # check that label field was defined in the post header
        if 'label' not in request.data:
            return Response({'label': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # check that the new value is unique to other
        for index, sensor in enumerate(node.sensors):
            if str(sensor.id) == sensorid:
                tmp_sensors[index].label = request.data.get('label')
                continue

            if sensor.label == request.data.get('label'):
                return Response({'label': 'This field must be unique.'}, status=status.HTTP_400_BAD_REQUEST)

        node.sensors = tmp_sensors
        node.save()
        return Response(SensorSerializer(
                tmp_sensors, many=True, context={'request': request}
            ).data, status=status.HTTP_201_CREATED
        )

    @staticmethod
    def delete(request, pk, sensorid):
        Nodes.objects(pk=pk).update_one(pull__sensors__id=sensorid)
        return Response(status=status.HTTP_204_NO_CONTENT)