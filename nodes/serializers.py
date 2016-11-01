from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from nodes.models import Nodes


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects)
    label = serializers.CharField(
        min_length=4, max_length=28,
        validators=[UniqueValidator(queryset=Nodes.objects.all())]
    )
    secretkey = serializers.CharField(max_length=16, write_only=True)
    subsperday = serializers.IntegerField()
    subsperdayremain = serializers.IntegerField(default=0)
    # extra field
    sensors_list = serializers.HyperlinkedIdentityField(
        view_name='node-sensor-detail',
        lookup_field='pk'
    )
    subscriptions_list = serializers.HyperlinkedIdentityField(
        view_name='subscription-filter-node',
        lookup_field='label',
        lookup_url_kwarg='node'
    )

    class Meta:
        model = Nodes
        fields = ('id', 'url', 'user', 'label', 'secretkey', 'subsperday', 'subsperdayremain', 'sensors_list',
                  'subscriptions_list')

    def create(self, validated_data):
        node = Nodes.objects.create(**validated_data)
        node.subsperdayremain = node.subsperday
        node.save()
        return node

    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.secretkey = validated_data.get('secretkey', instance.secretkey)
        instance.subsperday = validated_data.get('subsperday', instance.subsperday)
        instance.subsperdayremain = validated_data.get('subsperday', instance.subsperday)
        instance.save()
        return instance
