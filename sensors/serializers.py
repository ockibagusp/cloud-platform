from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer
from nodes.models import Nodes
from sensors.models import Sensors


class SensorSerializer(EmbeddedDocumentSerializer):
    label = serializers.CharField(
        min_length=4, max_length=28
    )
    # extra field
    url = serializers.SerializerMethodField()
    nodeurl = serializers.SerializerMethodField()
    subscriptions_list = serializers.SerializerMethodField()

    class Meta:
        model = Sensors
        fields = '__all__'

    def get_url(self, obj):
        return reverse('node-sensor-detail', args=[
                self.context.get('nodeid'), obj.label
            ], request=self.context['request']
        )

    def get_nodeurl(self, obj):
        return reverse('nodes-detail', args=[
                self.context.get('nodeid')
            ], request=self.context['request']
        )

    def get_subscriptions_list(self, obj):
        node = Nodes.objects.get(pk=self.context.get('nodeid'))
        return reverse('subscription-filter-node-sensor', args=[node.label, obj.label],
                       request=self.context['request'])

    def validate_label(self, value):
        node_id = self.context.get('nodeid')

        try:
            Nodes.objects.get(pk=node_id, sensors__label=value)
        except Nodes.DoesNotExist:
            return value
        raise serializers.ValidationError("This field must be unique.")