from collections import OrderedDict
from rest_framework import serializers
from rest_framework.fields import ListField
from subscriptions.models import Subscriptions
from nodes.models import Nodes
from sensors.models import Sensors
from datetime import date


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    node = serializers.SlugRelatedField(slug_field="label", queryset=Nodes.objects)
    sensor = serializers.SlugRelatedField(slug_field="label", queryset=Sensors.objects)
    data = serializers.CharField(max_length=128)
    timestamp = serializers.DateTimeField(required=False)
    testing = serializers.BooleanField(required=False)

    class Meta:
        model = Subscriptions
        fields = ('id', 'url', 'node', 'sensor', 'data', 'timestamp', 'testing')
        extra_kwargs = {
            'url': {'view_name': 'subscription-detail', 'lookup_field': 'pk'}
        }

    def validate(self, data):
        super(SubscriptionSerializer, self).validate(data)
        node = data.get('node')
        now = date.today()
        thisdaysubs = Subscriptions.objects.filter(
            timestamp__day=now.day, timestamp__month=now.month, timestamp__year=now.year, node__label=node.label
        )

        ''' reset Nodes subsperdayremain '''
        if not thisdaysubs:
            node.subsperdayremain = node.subsperday

        ''' check if node has remaining subscription this day '''
        if 0 != node.subsperdayremain:
            return data
        raise serializers.ValidationError('Subscription is limit.')

    def create(self, validated_data):
        node = validated_data.get('node')
        sensor = validated_data.get('sensor')

        ''' create new Subscription instance '''
        subs = Subscriptions()
        subs.node = node
        subs.sensor = sensor
        subs.data = validated_data.get('data')
        if not validated_data.get('testing'):
            subs.save()
        return subs


class SubscriptionFormatSerializer(serializers.ModelSerializer):
    node = serializers.SlugRelatedField(slug_field="label", queryset=Nodes.objects)
    sensor = ListField()
    testing = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Subscriptions
        fields = ('node', 'sensor', 'testing')

    """ validating that reffered object sensor is exist. """

    @staticmethod
    def issensorexist(nodelabel, sensorlabel):
        try:
            return Sensors.objects.get(label=sensorlabel, nodes__label=nodelabel)
        except Sensors.DoesNotExist:
            return False

    def validate(self, data):
        super(SubscriptionFormatSerializer, self).validate(data)
        errors = OrderedDict()
        ''' append error when list sensor is empty '''
        if not data.get('sensor'):
            errors['sensor'] = "Expected a dict contains \"label\" and \"data\" but got None"
        else:
            ''' validating inner sensor dict '''
            sensorerror = []
            for index, sensor in enumerate(data.get('sensor')):
                ''' append error when reffered object sensor is not exist '''
                if not self.issensorexist(data.get('node').label, sensor.get('label')):
                    sensorerror.append(
                        "sensor[%d]: Object with label=%s does not exist." % (index, sensor.get('label'))
                    )
            else:
                if sensorerror:
                    errors['sensor'] = sensorerror

        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        node = validated_data.get('node')
        sensors = validated_data.get('sensor')
        istesting = validated_data.get('testing')
        newsensors = []
        for sensor in sensors:
            data = {'node': node, 'sensor': node.sensors_set.get(label=sensor.get('label')),
                    'data': sensor.get('data'), 'testing': istesting}
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                subs = serializer.save()
                newsensors.append(subs)
            else:
                raise serializers.ValidationError(serializer.errors)
        if not istesting:
            ''' decrement Nodes subsperdayremain '''
            node.subsperdayremain -= 1
            node.save()
        return newsensors
