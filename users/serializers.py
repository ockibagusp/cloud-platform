from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework_mongoengine.validators import UniqueValidator
from users.models import User
from authenticate.authentication import make_password


class UserSerializer(DocumentSerializer):
    # override
    username = serializers.CharField(
        min_length=4, max_length=16,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Already taken!")]
    )
    password = serializers.CharField(max_length=16, write_only=True)
    # extra field
    url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='pk'
    )

    '''
    overide validate to hashing user password
    '''

    @staticmethod
    def validate_password(value):
        return make_password(value)

    class Meta:
        model = User
        fields = '__all__'
