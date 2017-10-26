from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsAuthenticated, IsUser
from sensordatas.models import Sensordatas
from sensordatas.serializers import SensordataSerializer, SensordataFormatSerializer
from nodes.models import Nodes
from supernodes.models import Supernodes
from helpers import SensordatasService


class SensordatasList(ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Sensordatas.objects.all()
    serializer_class = SensordataSerializer

    @staticmethod
    def post(request):
        # ensure that only nodes(provided by JWT credentials) can perform this action
        if not isinstance(request.user, Supernodes):
            raise exceptions.PermissionDenied("You do not have permission to perform this action.")

        # TODO validate node pubsperdayremain
        # if 0 == request.user.pubsperdayremain:
        #     raise exceptions.PermissionDenied("Publish is limit.")

        # validate POST payload format
        serformat = SensordataFormatSerializer(data=request.data, context={'request': request})
        if serformat.is_valid():
            message = serformat.save()
            return Response(
                {"results": message},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serformat.errors, status=status.HTTP_400_BAD_REQUEST)


class SensordatasDetail(GenericAPIView):
    """
    Retrieve, update or delete a Subscription instance.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)

    @staticmethod
    def get_object(pk):
        try:
            return Sensordatas.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get(self, request, pk, format=None):
        subs = self.get_object(pk)
        serializer = SensordataSerializer(subs, context={'request': request})
        return Response(serializer.data)


class SensordatasFilterUser(ListAPIView):

    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)

    def get(self, request, *args, **kwargs):
        return Response(SensordatasService().getbyuser(request))


class SensordatasFilterNode(ListAPIView):
    """
    Retrieve Subscription instance with node filtering.
    @url /sensordatas/node/<node-id>

    Filtering by subs date:
    @query ?start=<date-time>&&end=<date-time>

    From to Last filter
    @query ?start=2016-11-24 16:00:00&&end=2016-12-24 16:00:00

    From to ... filter
    @query ?start=2016-11-24 16:00:00

    ... to Last filter
    From to Last filter
    @query ?end=2016-12-24 16:00:00
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = SensordataSerializer

    @staticmethod
    def checknode(pk):
        """
        Raise error when Nodes is not exist.
        """
        try:
            return Nodes.objects.get(pk=pk)
        except Exception:
            raise NotFound(detail="Nodes with id=%s does not exist." % pk)

    def get_queryset(self):
        """
        This view should return a list of all the subscription for
        the node as determined by the node portion of the URL.
        """
        nodeid = self.kwargs['node']
        node = self.checknode(nodeid)
        if self.request.user != node.user and 0 == node.is_public:
            return 'unauthorized'

        filter_from = self.request.GET.get('start')
        filter_last = self.request.GET.get('end')

        if filter_from and filter_last:
            return Sensordatas.objects.filter(
                node=node, timestamp__gte=filter_from, timestamp__lte=filter_last
            )
        elif filter_from:
            return Sensordatas.objects.filter(node=node, timestamp__gte=filter_from)
        elif filter_last:
            return Sensordatas.objects.filter(node=node, timestamp__lte=filter_last)
        else:
            return Sensordatas.objects.filter(node=node)

    def get(self, request, *args, **kwargs):
        raw_queryset = self.get_queryset()
        if 'unauthorized' == raw_queryset:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        queryset = self.filter_queryset(raw_queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SensordataSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SensordatasFilterNodeSensor(ListAPIView):
    """
    Retrieve Subscription instance with node and sensor filtering.
    @url /sensordatas/node/<node-label>/sensor/<sensor-label>

    Filtering by subs date:
    @query ?start=<date-time>&&end=<date-time>

    From to Last filter
    @query ?start=2016-11-24 16:00:00&&end=2016-12-24 16:00:00

    From to ... filter
    @query ?start=2016-11-24 16:00:00

    ... to Last filter
    From to Last filter
    @query ?end=2016-12-24 16:00:00
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = SensordataSerializer

    def checknode(self, node, sensor):
        """
        Raise error when Nodes is not exist.
        """
        try:
            node = Nodes.objects.get(pk=node)
            sensor = self.checksensor(node, sensor)
            return {
                'node': node,
                'sensor': sensor
            }
        except Nodes.DoesNotExist:
            raise NotFound(detail="Nodes with id=%s does not exist." % node)

    @staticmethod
    def checksensor(node, sensorlabel):
        """
        Raise error when Sensors is not exist.
        """
        try:
            return node.sensors.get(id=sensorlabel)
        except Exception:
            raise NotFound(detail="Sensors with id=%s does not exist." % sensorlabel)

    def get_queryset(self):
        """
        This view should return a list of all the sensordatas for
        the node as determined by the node portion of the URL.
        """
        nodelabel = self.kwargs['node']
        sensorlabel = self.kwargs['sensor']

        node_sensor = self.checknode(nodelabel, sensorlabel)
        if self.request.user != node_sensor.get('node').user and 0 == node_sensor.get('node').is_public:
            return 'unauthorized'

        filter_from = self.request.GET.get('start')
        filter_last = self.request.GET.get('end')

        if filter_from and filter_last:
            return Sensordatas.objects.filter(
                node=node_sensor.get('node').id, sensor=node_sensor.get('sensor').id,
                timestamp__gte=filter_from, timestamp__lte=filter_last
            )
        elif filter_from:
            return Sensordatas.objects.filter(
                node=node_sensor.get('node').id, sensor=node_sensor.get('sensor').id,
                timestamp__gte=filter_from
            )
        elif filter_last:
            return Sensordatas.objects.filter(
                node=node_sensor.get('node').id, sensor=node_sensor.get('sensor').id,
                timestamp__lte=filter_last
            )
        else:
            return Sensordatas.objects.filter(node=node_sensor.get('node').id, sensor=node_sensor.get('sensor').id)

    def get(self, request, *args, **kwargs):
        raw_queryset = self.get_queryset()
        if 'unauthorized' == raw_queryset:
            return Response({
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        queryset = self.filter_queryset(raw_queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SensordataSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
