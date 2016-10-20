from rest_framework import serializers
from subscriptions.models import Subscriptions
from nodes.models import Nodes
from sensors.models import Sensors


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    node = serializers.ReadOnlyField(source="node.label")
    sensor = serializers.ReadOnlyField(source="sensor.label")
    data = serializers.CharField(max_length=128)
    timestamp = serializers.DateTimeField(required=False)

    class Meta:
        model = Sensors
        fields = ('id', 'node', 'sensor', 'data', 'timestamp')

    def create(self, validated_data):
        node = Nodes.objects.get(label=self.context['request'].data['node'].get('label'))
        sensor = Sensors.objects.get(label=self.context['request'].data['sensor'].get('label'))
        subs = Subscriptions()
        subs.node = node
        subs.sensor = sensor
        subs.data = validated_data.get('data')
        subs.save()
        return subs
