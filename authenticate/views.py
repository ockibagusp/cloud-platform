import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authenticate.forms import SuperNodeAuthForm, UserAuthForm
from authenticate.utils import supernode_jwt_payload_handler, user_jwt_payload_handler
from authenticate.serializers import UserSerializer
from supernodes.serializers import SuperNodesSerializer
from cloud_platform import settings


class UserTokenCreator(APIView):
    """
    Create token if user credentials was provided and valid.
    """

    def post(self, request, format=None):
        form = UserAuthForm(request.data)
        if form.is_valid():
            return Response({
                'user': UserSerializer(form.user).data,
                'token': self.create_token(form.user)
            })
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_token(user):
        payload = user_jwt_payload_handler(user)
        token = jwt.encode(payload, settings.SECRET_KEY)
        return token.decode('unicode_escape')


class NodeTokenCreator(APIView):
    """
    Create token if node credentials was provided and valid.
    """

    def post(self, request, format=None):
        form = SuperNodeAuthForm(request.data)
        if form.is_valid():
            return Response({
                'supernode': SuperNodesSerializer(form.supernode, context={'request': request}).data,
                'token': self.create_token(form.supernode)
            })
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_token(node):
        payload = supernode_jwt_payload_handler(node)
        token = jwt.encode(payload, settings.SECRET_KEY)
        return token.decode('unicode_escape')

