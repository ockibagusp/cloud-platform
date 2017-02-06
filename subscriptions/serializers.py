from collections import OrderedDict
from rest_framework import serializers
from rest_framework.fields import ListField
from rest_framework.reverse import reverse
from rest_framework_mongoengine.serializers import DocumentSerializer
from subscriptions.models import Subscriptions
from nodes.models import Nodes
from users.models import User
from datetime import date, datetime


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
        now = date.today()
        beginday = datetime(now.year, now.month, now.day, 0, 0, 0)
        endday = datetime(now.year, now.month, now.day, 23, 59, 0)

        thisdaysubs = Subscriptions.objects.filter(
            timestamp__gte=beginday, timestamp__lte=endday, node=node.id
        )

        ''' -1 means node has not subscription limit '''
        if -1 is node.subsperday:
            return data

        ''' reset Nodes subsperdayremain '''
        if not thisdaysubs:
            node.subsperdayremain = node.subsperday
            node.save()

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
    user = serializers.CharField(max_length=28)
    node = serializers.CharField(max_length=28)
    sensor = ListField()
    testing = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Subscriptions
        fields = ('user', 'node', 'sensor', 'testing')

    """ ensure that reffered object user is exist. """

    @staticmethod
    def isuserexist(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return False

    """ ensure that reffered object sensor is exist. """

    @staticmethod
    def isnodeexist(nodelabel, userid):
        try:
            return Nodes.objects.get(user=userid, label=nodelabel)
        except Nodes.DoesNotExist:
            return False

    @staticmethod
    def issensorexist(nodesensors, sensorlabel):
        try:
            return nodesensors.get(label=sensorlabel)
        except Exception:
            return False

    def validate(self, data):
        super(SubscriptionFormatSerializer, self).validate(data)
        errors = OrderedDict()

        user = self.isuserexist(data.get('user'))
        if not user:
            errors['user'] = 'User with username=%s does not exist.' % data.get('user')
            raise serializers.ValidationError(errors)

        node = self.isnodeexist(data.get('node'), user.id)
        if not node:
            errors['node'] = "Nodes with label=%s does not exist. " \
                             "Or ensure that 'user' and 'node' field is match" % data.get('node')
            raise serializers.ValidationError(errors)

        ''' append error when list sensor is empty '''
        if not data.get('sensor'):
            errors['sensor'] = "Expected a dict contains \"label\" and \"data\" but got None"
        else:
            ''' validating inner sensor dict '''
            sensorerror = []
            labelerror = []
            for index, sensor in enumerate(data.get('sensor')):
                ''' append error when reffered object sensor is not exist '''
                if not self.issensorexist(node.sensors, sensor.get('label')):
                    sensorerror.append(
                        "sensor[%d]: Object with label=%s does not exist." % (index, sensor.get('label'))
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
        node = Nodes.objects.get(label=validated_data.get('node'))
        sensors = validated_data.get('sensor')
        istesting = validated_data.get('testing')
        newsensors = []
        for sensor in sensors:
            data = {'node': node.label, 'sensor': node.sensors.get(label=sensor.get('label')).id,
                    'data': sensor.get('data'), 'testing': istesting}
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                subs = serializer.save()
                newsensors.append(subs)
            else:
                raise serializers.ValidationError(serializer.errors)
        if not istesting:
            node = Nodes.objects.get(label=validated_data.get('node'))
            ''' decrement Nodes subsperdayremain when node has subscription limit '''
            if -1 is not node.subsperday:
                node.subsperdayremain -= 1
            node.save()
        return newsensors
