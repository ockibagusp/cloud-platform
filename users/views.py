from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine.generics import ListAPIView, GenericAPIView
from authenticate.authentication import JSONWebTokenAuthentication
from authenticate.permissions import IsAdmin
from users.models import User
from users.serializers import UserSerializer


class UsersList(ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdmin,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(GenericAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdmin,)

    @staticmethod
    def get_user(pk):
        try:
            return User.objects.get(pk=pk)
        except Exception:
            raise Http404

    def get(self, request, pk):
        user = self.get_user(pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_user(pk)
        # ensure that super admin only edited by him/his self
        if "webmaster" == user.username:
            return Response({
                'detail': 'You can not update super admin user data.'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_user(pk)
        # super admin can not be deleted
        if "webmaster" == user.username:
            return Response({
                'detail': 'Super admin can not be deleted.'
            }, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
