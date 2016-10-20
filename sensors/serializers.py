from rest_framework import serializers
from sensors.models import Sensors
from nodes.serializers import NodeSerializer


class SensorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    label = serializers.CharField(min_length=4, max_length=28)
    nodes = NodeSerializer()

    class Meta:
        model = Sensors
        fields = ('id', 'nodes', 'label',)
