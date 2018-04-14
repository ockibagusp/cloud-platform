from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer
from supernodes.models import Supernodes
from nodes.models import Nodes
from sensors.models import Sensors


class SupernodeSensorSerializer(EmbeddedDocumentSerializer):
    label = serializers.CharField(
        min_length=4, max_length=28
    )
    # extra field
    url = serializers.SerializerMethodField()
    supernodeurl = serializers.SerializerMethodField()
    # sensordatas_list = serializers.SerializerMethodField()

    class Meta:
        model = Sensors
        fields = '__all__'

    def get_url(self, obj):
        # when serialize existing Sensor obj
        if isinstance(obj, Sensors):
            sensorid = obj.id
        else:  # when create new Sensor obj
            sensorid = obj.get('id')

        return reverse('supernodes-sensors-detail', args=[
            self.context.get('supernodeid'), sensorid
        ], request=self.context['request']
                       )

    def get_supernodeurl(self, obj):
        return reverse('supernodes-detail', args=[
            self.context.get('supernodeid')
        ], request=self.context['request']
                       )

    def get_sensordatas_list(self, obj):
        # when serialize existing Sensor obj
        if isinstance(obj, Sensors):
            sensorlabel = obj.label
        else:  # when create new Sensor obj
            sensorlabel = self.context['request'].data.get('label')

        supernode = Supernodes.objects.get(pk=self.context.get('supernodeid'))
        return reverse('sensordata-filter-supernode-sensor', args=[supernode.label, sensorlabel],
                       request=self.context['request'])

    def validate_label(self, value):
        supernode_id = self.context.get('supernodeid')

        try:
            Supernodes.objects.get(pk=supernode_id, sensors__label=value)
        except Supernodes.DoesNotExist:
            # when create new sensor instance
            return value
        if self.context.get('isupdate'):
            # when update sensor instance
            return value
        else:
            raise serializers.ValidationError("This field must be unique.")


class NodeSensorSerializer(EmbeddedDocumentSerializer):
    label = serializers.CharField(
        min_length=4, max_length=28
    )
    # extra field
    url = serializers.SerializerMethodField()
    nodeurl = serializers.SerializerMethodField()
    sensordatas_list = serializers.SerializerMethodField()

    class Meta:
        model = Sensors
        fields = '__all__'

    def get_url(self, obj):
        # when serialize existing Sensor obj
        if isinstance(obj, Sensors):
            sensorid = obj.id
        else:  # when create new Sensor obj
            sensorid = obj.get('id')

        return reverse('node-sensor-detail', args=[
            self.context.get('nodeid'), sensorid
        ], request=self.context['request']
                       )

    def get_nodeurl(self, obj):
        return reverse('nodes-detail', args=[
            self.context.get('nodeid')
        ], request=self.context['request']
                       )

    def get_sensordatas_list(self, obj):
        # when serialize existing Sensor obj
        if isinstance(obj, Sensors):
            sensorlabel = obj.label
        else:  # when create new Sensor obj
            sensorlabel = self.context['request'].data.get('label')

        node = Nodes.objects.get(pk=self.context.get('nodeid'))
        return reverse('sensordata-filter-node-sensor', args=[node.label, sensorlabel],
                       request=self.context['request'])

    def validate_label(self, value):
        node_id = self.context.get('nodeid')

        try:
            Nodes.objects.get(pk=node_id, sensors__label=value)
        except Nodes.DoesNotExist:
            # when create new sensor instance
            return value
        if self.context.get('isupdate'):
            # when update sensor instance
            return value
        else:
            raise serializers.ValidationError("This field must be unique.")