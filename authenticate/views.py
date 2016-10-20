import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authenticate.forms import AuthForm
from authenticate.utils import jwt_payload_handler
from nodes.serializers import NodeSerializer
from cloud_gateway import settings


class TokenCreator(APIView):
    """
    Create token if node credentials was provided and valid.
    """

    def post(self, request, format=None):
        form = AuthForm(request.data)
        if form.is_valid():
            return Response({
                'node': NodeSerializer(form.node).data,
                'token': self.create_token(form.node)
            })
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_token(node):
        payload = jwt_payload_handler(node)
        token = jwt.encode(payload, settings.SECRET_KEY)
        return token.decode('unicode_escape')

