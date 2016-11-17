from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_mongoengine.fields import ObjectIdField


class UserSerializer(serializers.ModelSerializer):
    id = ObjectIdField()
    username = serializers.CharField(min_length=5, max_length=15)
    password = serializers.CharField(min_length=8, max_length=15, write_only=True)
    email = serializers.CharField(max_length=254, required=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')