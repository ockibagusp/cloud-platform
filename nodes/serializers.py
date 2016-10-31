from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from nodes.models import Nodes


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    sensors_list = serializers.HyperlinkedIdentityField(
        view_name='node-sensor-detail',
        lookup_field='pk'
    )
    label = serializers.CharField(
        min_length=4, max_length=28,
        validators=[UniqueValidator(queryset=Nodes.objects.all())]
    )
    secretkey = serializers.CharField(max_length=16, write_only=True)
    subsperday = serializers.IntegerField()
    subsperdayremain = serializers.IntegerField(default=0)

    class Meta:
        model = Nodes
        fields = ('id', 'url', 'label', 'secretkey', 'subsperday', 'subsperdayremain', 'sensors_list')

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
