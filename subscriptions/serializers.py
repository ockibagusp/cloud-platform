from collections import OrderedDict
from rest_framework import serializers
from rest_framework.fields import ListField
from rest_framework.reverse import reverse
from rest_framework_mongoengine.serializers import DocumentSerializer
from subscriptions.models import Subscriptions
from nodes.models import Nodes


class SubscriptionSerializer(DocumentSerializer):
    node = serializers.SlugRelatedField(slug_field="label", queryset=Nodes.objects)
    # extra field
    testing = serializers.BooleanField(required=False)
    url = serializers.SerializerMethodField()
    nodeurl = serializers.SerializerMethodField(method_name='getnodeurl')
    sensorurl = serializers.SerializerMethodField(method_name='getsensorurl')
    sensorlabel = serializers.SerializerMethodField(method_name='getsensorlabel')

    class Meta:
        model = Subscriptions
        fields = '__all__'

    def get_url(self, obj):
        return reverse('subscription-detail', args=[obj.id], request=self.context['request'])

    def getnodeurl(self, obj):
        return reverse('nodes-detail', args=[obj.node.pk], request=self.context['request'])

    def getsensorurl(self, obj):
        return reverse('node-sensor-detail', args=[obj.node.pk, str(obj.sensor)], request=self.context['request'])

    @staticmethod
    def getsensorlabel(obj):
        obj.node.sensors.get(id=obj.sensor)
        return obj.node.sensors.get(id=obj.sensor).label

    def validate(self, data):
        super(SubscriptionSerializer, self).validate(data)
        node = data.get('node')

        ''' -1 means node has not subscription limit '''
        if -1 is node.subsperday:
            return data

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


class SubscriptionFormatSerializer(DocumentSerializer):
    publish = ListField()
    testing = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Subscriptions
        fields = ('publish', 'testing')

    """ ensure that reffered object sensor is exist. """

    @staticmethod
    def get_node(node):
        try:
            return Nodes.objects.get(id=node.id)
        except Nodes.DoesNotExist:
            return False

    @staticmethod
    def get_node_sensor(nodesensors, sensorlabel):
        try:
            return nodesensors.get(label=sensorlabel)
        except Exception:
            return False

    def validate(self, data):
        super(SubscriptionFormatSerializer, self).validate(data)
        errors = OrderedDict()

        node = self.get_node(self.context.get('request').user)

        ''' append error when list sensor is empty '''
        if not data.get('publish'):
            errors['publish'] = "Expected a dict contains \"sensor\" and \"data\" but got None"
        else:
            ''' validating inner publish dict '''
            sensorerror = []
            labelerror = []
            for index, sensor in enumerate(data.get('publish')):
                ''' append error when reffered object sensor is not exist '''
                if not self.get_node_sensor(node.sensors, sensor.get('sensor')):
                    sensorerror.append(
                        "sensor[%d]: Object with label=%s does not exist." % (index, sensor.get('sensor'))
                    )
                if not sensor.get('data'):
                    labelerror.append(
                        "label[%d]: This field may not be null." % index
                    )
            else:
                if sensorerror:
                    errors['sensor'] = sensorerror
                if labelerror:
                    errors['label'] = labelerror

        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        node = self.get_node(self.context.get('request').user)
        publishes = validated_data.get('publish')
        istesting = validated_data.get('testing')
        newsensors = []
        for publish in publishes:
            data = {'node': node.label, 'sensor': node.sensors.get(label=publish.get('sensor')).id,
                    'data': publish.get('data'), 'testing': istesting}
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                subs = serializer.save()
                newsensors.append(subs)
            else:
                raise serializers.ValidationError(serializer.errors)
        if not istesting:
            ''' decrement Nodes subsperdayremain when node has subscription limit '''
            if -1 is not node.subsperday:
                node.subsperdayremain -= 1
            node.save()
        return newsensors
