from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from nodes.models import Nodes
from sensors.models import Sensors
from subscriptions.models import Subscriptions
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

    def post(self, request, pk):
        # validate nodeid in url kwargs
        self.get_object(pk)
        serializer = SensorSerializer(data=request.data, context={
            'request': request, 'nodeid': pk
        })

        if serializer.is_valid():
            node = Nodes.objects(pk=pk)
            """
            ObjectId for new sensor must generate before save the instance
            """
            import bson
            newid = bson.objectid.ObjectId()
            node.update_one(
                push__sensors=Sensors(id=newid, label=serializer.data.get('label'))
            )
            """
            Get sensor data manually and serialize it again.
            Using serializer.data directly will raise ObjectID error cause
            EmbededDocument, normally, doesn`t have _id field.
            """
            sensor = node.first().sensors.get(label=serializer.data.get('label'))
            return Response(SensorSerializer(
                sensor, context={'request': request, 'nodeid': pk}
            ).data, status=status.HTTP_201_CREATED)
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
        self_sensor = Sensors()

        # check that label field was defined in the post header
        if 'label' not in request.data:
            return Response({'label': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # check that the new value is unique to other
        for index, sensor in enumerate(node.sensors):
            if str(sensor.id) == sensorid:
                tmp_sensors[index].label = request.data.get('label')
                self_sensor = tmp_sensors[index]
                continue

            if sensor.label == request.data.get('label'):
                return Response({'label': 'This field must be unique.'}, status=status.HTTP_400_BAD_REQUEST)

        node.sensors = tmp_sensors
        node.save()
        return Response(SensorSerializer(
                self_sensor, context={'request': request, 'nodeid': pk}
            ).data, status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk, sensorid):
        # check that nodeid and sensorid is valid
        self.get_node(pk, sensorid)
        Nodes.objects(pk=pk).update_one(pull__sensors__id=sensorid)
        # delete referer subscription
        Subscriptions.objects(sensor=sensorid).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)