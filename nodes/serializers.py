from rest_framework import serializers
from nodes.models import Nodes


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    sensors_list = serializers.HyperlinkedIdentityField(
        view_name='node-sensor-detail',
        lookup_field='pk'
    )
    label = serializers.CharField(min_length=4, max_length=28)
    secretkey = serializers.CharField(max_length=16, write_only=True)
    subsperday = serializers.IntegerField(default=0)
    subsperdayremain = serializers.IntegerField(default=0)

    class Meta:
        model = Nodes
        fields = ('id', 'url', 'label', 'secretkey', 'subsperday', 'subsperdayremain', 'sensors_list')
