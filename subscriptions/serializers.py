from rest_framework import serializers
from subscriptions.models import Subscriptions
from nodes.models import Nodes
from sensors.models import Sensors
from datetime import date


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    node = serializers.ReadOnlyField(source="node.label")
    sensor = serializers.ReadOnlyField(source="sensor.label")
    data = serializers.CharField(max_length=128)
    timestamp = serializers.DateTimeField(required=False)

    class Meta:
        model = Sensors
        fields = ('id', 'node', 'sensor', 'data', 'timestamp')

    def validate(self, data):
        super(SubscriptionSerializer, self).validate(data)
        node = Nodes.objects.get(label=self.context['request'].data['node'].get('label'))
        # node = Nodes.objects.get(label="FILKOM_1")
        now = date.today()
        thisdaysubs = Subscriptions.objects.filter(
            timestamp__day=now.day, timestamp__month=now.month, timestamp__year=now.year, node__label=node.label
        )

        ''' reset Nodes subsperdayremain '''
        lastnodesubs = thisdaysubs[0].timestamp
        if lastnodesubs.strftime('%d-%m-%Y') < now.strftime('%d-%m-%Y'):
            node.subsperdayremain = node.subsperday

        ''' check if node has remaining subscription this day '''
        if 0 != node.subsperdayremain:
            return data
        raise serializers.ValidationError('Subscription is limit.')

    def create(self, validated_data):
        node = Nodes.objects.get(label=self.context['request'].data['node'].get('label'))
        sensor = Sensors.objects.get(label=self.context['request'].data['sensor'].get('label'))

        ''' create new Subscription instance '''
        subs = Subscriptions()
        subs.node = node
        subs.sensor = sensor
        subs.data = validated_data.get('data')
        subs.save()

        ''' decrement Nodes subsperdayremain '''
        node.subsperdayremain -= 1
        node.save()
        return subs
