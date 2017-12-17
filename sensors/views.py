from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsUser
from cloud_platform.helpers import is_objectid_valid
from supernodes.models import Supernodes
from nodes.models import Nodes
from sensors.models import Sensors
from sensordatas.models import Sensordatas
from sensors.serializers import SupernodeSensorSerializer, NodeSensorSerializer


class SensorsList(ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = NodeSensorSerializer

    @staticmethod
    def get_object(pk):
        try:
            return Nodes.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get_queryset(self):
        node = self.get_object(self.kwargs.get('pk'))
        return node

    def get(self, request, *args, **kwargs):
        # return node query set
        queryset = self.filter_queryset(self.get_queryset())
        # no access to another user private node
        if request.user != queryset.user and 0 == queryset.is_public:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(queryset.sensors)
        if page is not None:
            serializer = NodeSensorSerializer(page, many=True, context={
                'request': request, 'nodeid': kwargs.get('pk')
            })
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        # validate nodeid in url kwargs
        node = self.get_object(pk)
        # no access to another user private node
        if request.user != node.user and 0 == node.is_public:
            return Response({
                'detail': 'You can not create sensor for another person node.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = NodeSensorSerializer(data=request.data, context={
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
            return Response(NodeSensorSerializer(
                sensor, context={'request': request, 'nodeid': pk}
            ).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SensorDetail(GenericAPIView):
    """
    Retrieve, update or delete a Sensor instance.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)

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
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        data = self.get_node(pk, sensorid)
        # no access to another user private node
        if request.user != data.get('node').user and 0 == data.get('node').is_public:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = NodeSensorSerializer(data.get('sensor'), context={'request': request, 'nodeid': pk})
        return Response(serializer.data)

    def put(self, request, pk, sensorid):
        # check that label field was defined in the post header
        if 'label' not in request.data:
            return Response({'label': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)

        """
        Manual validation
        cause any selializer cannot handle EmbededDocummentList update
        """
        data = self.get_node(pk, sensorid)
        node = data.get('node')
        serializer = NodeSensorSerializer(data=request.data, context={
            'request': request, 'nodeid': pk, 'isupdate': True
        }, partial=True)

        if serializer.is_valid():
            tmp_sensors = data.get('node').sensors
            self_sensor = Sensors()

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
            return Response(
                NodeSensorSerializer(
                    self_sensor, context={'request': request, 'nodeid': pk}
                ).data, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, sensorid):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        # check that nodeid and sensorid is valid
        data = self.get_node(pk, sensorid)
        # no access to delete another user sensor node
        if request.user != data.get('node').user:
            return Response({
                'detail': 'You can not delete another person node.'
            }, status=status.HTTP_403_FORBIDDEN)

        Nodes.objects(pk=pk).update_one(pull__sensors__id=sensorid)
        # delete referer subscription
        Sensordatas.objects(sensor=sensorid).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupernodeSensorsList(ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = SupernodeSensorSerializer

    @staticmethod
    def get_object(pk):
        try:
            return Supernodes.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get_queryset(self):
        supernode = self.get_object(self.kwargs.get('pk'))
        return supernode

    def get(self, request, *args, **kwargs):
        # return node query set
        queryset = self.filter_queryset(self.get_queryset())
        # TODO supernode visibility?
        # no access to another user private node
        if request.user != queryset.user and 0 == queryset.is_public:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(queryset.sensors)
        if page is not None:
            serializer = SupernodeSensorSerializer(page, many=True, context={
                'request': request, 'supernodeid': kwargs.get('pk')
            })
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        # validate nodeid in url kwargs
        supernode = self.get_object(pk)
        # no access to another user private supernode
        # TODO supernode visibility?
        if request.user != supernode.user and 0 == supernode.is_public:
            return Response({
                'detail': 'You can not create sensor for another person supernode.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = SupernodeSensorSerializer(data=request.data, context={
            'request': request, 'supernodeid': pk
        })

        if serializer.is_valid():
            supernode = Supernodes.objects(pk=pk)
            """
            ObjectId for new sensor must generate before save the instance
            """
            import bson
            newid = bson.objectid.ObjectId()
            supernode.update_one(
                push__sensors=Sensors(id=newid, label=serializer.data.get('label'))
            )
            """
            Get sensor data manually and serialize it again.
            Using serializer.data directly will raise ObjectID error cause
            EmbededDocument, normally, doesn`t have _id field.
            """
            sensor = supernode.first().sensors.get(label=serializer.data.get('label'))
            return Response(SupernodeSensorSerializer(
                sensor, context={'request': request, 'supernodeid': pk}
            ).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupernodeSensorDetail(GenericAPIView):
    """
    Retrieve, update or delete a Sensor instance.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)

    @staticmethod
    def get_supernode(supernode_pk, sensor_id):
        try:
            supernode = Supernodes.objects.get(pk=supernode_pk)
            sensor = supernode.sensors.get(id=sensor_id)
            return {
                'supernode': supernode,
                'sensor': sensor
            }
        except Exception:
            raise Http404

    def get(self, request, pk, sensorid):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        data = self.get_supernode(pk, sensorid)
        # TODO supernode visibility?
        # no access to another user private node
        if request.user != data.get('supernode').user and 0 == data.get('supernode').is_public:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = SupernodeSensorSerializer(data.get('sensor'), context={'request': request, 'supernodeid': pk})
        return Response(serializer.data)

    def put(self, request, pk, sensorid):
        # check that label field was defined in the post header
        if 'label' not in request.data:
            return Response({'label': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)

        """
        Manual validation
        cause any selializer cannot handle EmbededDocummentList update
        """
        data = self.get_supernode(pk, sensorid)
        supernode = data.get('supernode')
        serializer = SupernodeSensorSerializer(data=request.data, context={
            'request': request, 'supernodeid': pk, 'isupdate': True
        }, partial=True)

        if serializer.is_valid():
            tmp_sensors = data.get('supernode').sensors
            self_sensor = Sensors()

            # check that the new value is unique to other
            for index, sensor in enumerate(supernode.sensors):
                if str(sensor.id) == sensorid:
                    tmp_sensors[index].label = request.data.get('label')
                    self_sensor = tmp_sensors[index]
                    continue

                if sensor.label == request.data.get('label'):
                    return Response({'label': 'This field must be unique.'}, status=status.HTTP_400_BAD_REQUEST)

            supernode.sensors = tmp_sensors
            supernode.save()
            return Response(
                SupernodeSensorSerializer(
                    self_sensor, context={'request': request, 'supernodeid': pk}
                ).data, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, sensorid):
        if not is_objectid_valid(pk):
            return Response({
                'detail': '%s is not valid ObjectId.' % pk
            }, status=status.HTTP_400_BAD_REQUEST)
        # check that nodeid and sensorid is valid
        data = self.get_supernode(pk, sensorid)
        # no access to delete another user sensor node
        if request.user != data.get('supernode').user:
            return Response({
                'detail': 'You can not delete another person node.'
            }, status=status.HTTP_403_FORBIDDEN)

        Supernodes.objects(pk=pk).update_one(pull__sensors__id=sensorid)
        # delete referer subscription
        Sensordatas.objects(sensor=sensorid).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)