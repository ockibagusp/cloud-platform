from collections import OrderedDict

from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer
from users.models import User
from nodes.models import Nodes
from supernodes.models import Supernodes, Coordinates


class SuperNodesSerializer(DocumentSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects)
    label = serializers.CharField(min_length=2, max_length=28)
    description = serializers.CharField(max_length=140, required=False, allow_null=True)
    # extra field
    url = serializers.HyperlinkedIdentityField(
        view_name='supernodes-detail',
        lookup_field='pk'
    )
    sensor_count = serializers.SerializerMethodField()
    node_count = serializers.SerializerMethodField()
    nodes_list = serializers.HyperlinkedIdentityField(
        view_name='supernodes-node-list',
        lookup_field='pk'
    )

    class Meta:
        model = Supernodes
        exclude = ('sensors',)

    @staticmethod
    def get_sensor_count(obj):
        return obj.sensors.count()

    @staticmethod
    def get_node_count(obj):
        return Nodes.objects.filter(supernode=obj).count()

    def validate_label(self, value):
        """
        rest_framework.validators.UniqueValidator can't handle label uniqueness
        if we just want to avoid the same label for a user and let it for other user instead.
        :param value: self.label
        :return: validated value
        """
        user = self.context.get('request').user
        supernode = Supernodes.objects.filter(user=user, label=value)

        # when updating instance
        if None is not self.instance:
            if not supernode or self.instance.label == value:
                return value
        elif not supernode:  # when create new instance
            return value
        raise serializers.ValidationError("This field must be unique.")

    def create(self, validated_data):
        supernode = Supernodes.objects.create(**validated_data)
        supernode.save()
        return supernode

    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.secretkey = validated_data.get('secretkey', instance.secretkey)
        instance.description = validated_data.get('description', instance.description)
        _coordinates = validated_data.get('coordinates', instance.coordinates)

        if isinstance(_coordinates, OrderedDict):
            _coordinates = Coordinates(lat=_coordinates['lat'], long=_coordinates['long'])

        instance.coordinates = _coordinates
        instance.save()
        return instance
