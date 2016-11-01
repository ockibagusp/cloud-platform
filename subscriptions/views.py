from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from rest_framework import exceptions
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsAuthenticated, IsUser
from sensors.models import Sensors
from subscriptions.models import Subscriptions
from subscriptions.serializers import SubscriptionSerializer, SubscriptionFormatSerializer
from nodes.models import Nodes
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class SubscriptionsList(ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionSerializer

    @staticmethod
    def post(request):
        if not isinstance(request.user, Nodes):
            raise exceptions.AuthenticationFailed("You do not have permission to perform this action.")

        serformat = SubscriptionFormatSerializer(data=request.data)
        if serformat.is_valid():
            data = serformat.save()
            return Response(
                SubscriptionSerializer(data, many=True, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serformat.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionDetail(APIView):
    """
    Retrieve, update or delete a Subscription instance.
    """

    @staticmethod
    def get_object(pk):
        try:
            return Subscriptions.objects.get(pk=pk)
        except Subscriptions.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        subs = self.get_object(pk)
        serializer = SubscriptionSerializer(subs, context={'request': request})
        return Response(serializer.data)


class SubscriptionFilterUser(ListAPIView):
    """
    Retrieve Subscription instance with user filtering.
    @url /subscriptions/user/<user-username>
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        """
        This view should return a list of all the subscriptions
        for the currently authenticated user.
        """
        user = self.request.user
        return Subscriptions.objects.filter(node__user=user)


class SubscriptionFilterNode(ListAPIView):
    """
    Retrieve Subscription instance with node filtering.
    @url /subscriptions/node/<node-label>
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = SubscriptionSerializer

    @staticmethod
    def checknode(label):
        """
        Raise error when Nodes is not exist.
        """
        try:
            return Nodes.objects.get(label=label)
        except Nodes.DoesNotExist:
            raise NotFound(detail="Nodes with label=%s does not exist." % label)

    def get_queryset(self):
        """
        This view should return a list of all the subscription for
        the node as determined by the node portion of the URL.
        """
        nodelabel = self.kwargs['node']
        self.checknode(nodelabel)
        return Subscriptions.objects.filter(node__label=nodelabel)


class SubscriptionFilterNodeSensor(ListAPIView):
    """
    Retrieve Subscription instance with node and sensor filtering.
    @url /subscriptions/node/<node-label>/sensor/<sensor-label>
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsUser,)
    serializer_class = SubscriptionSerializer

    @staticmethod
    def checknode(label):
        """
        Raise error when Nodes is not exist.
        """
        try:
            return Nodes.objects.get(label=label)
        except Nodes.DoesNotExist:
            raise NotFound(detail="Nodes with label=%s does not exist." % label)

    @staticmethod
    def checksensor(label):
        """
        Raise error when Sensors is not exist.
        """
        try:
            return Sensors.objects.get(label=label)
        except Sensors.DoesNotExist:
            raise NotFound(detail="Sensors with label=%s does not exist." % label)

    def get_queryset(self):
        """
        This view should return a list of all the subscription for
        the node as determined by the node portion of the URL.
        """
        nodelabel = self.kwargs['node']
        sensorlabel = self.kwargs['sensor']
        self.checknode(nodelabel)
        self.checksensor(sensorlabel)
        return Subscriptions.objects.filter(node__label=nodelabel, sensor__label=sensorlabel)