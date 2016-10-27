from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from rest_framework import exceptions
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsAuthenticated
from subscriptions.models import Subscriptions
from subscriptions.serializers import SubscriptionSerializer, SubscriptionFormatSerializer
from nodes.models import Nodes
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class SubscriptionsList(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request):
        subs = Subscriptions.objects.all()
        serializer = SubscriptionSerializer(subs, many=True, context={'request': request})
        return Response(serializer.data)

    @staticmethod
    def post(request):
        if not isinstance(request.user, Nodes):
            raise exceptions.AuthenticationFailed("You do not have permission to perform this action.")

        serformat = SubscriptionFormatSerializer(data=request.data)
        if serformat.is_valid():
            serializer = SubscriptionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # FIXME why node and sensor is 'unicode'?
                ser = serializer.save()
                return Response(
                    SubscriptionSerializer(ser, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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


class SubscriptionFilter(APIView):
    """
    Retrieve Subscription instance with node and sensor filtering.
    @url /subscriptions/<node-label>/<sensor-label>
    """

    @staticmethod
    def get_object(node, sensor):
        try:
            return Subscriptions.objects.filter(node__label=node, sensor__label=sensor)
        except Subscriptions.DoesNotExist:
            raise Http404

    def get(self, request, node, sensor, format=None):
        subs = self.get_object(node, sensor)
        serializer = SubscriptionSerializer(subs, many=True, context={'request': request})
        return Response(serializer.data)