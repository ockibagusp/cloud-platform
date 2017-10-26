from collections import OrderedDict
from bson import ObjectId
from bson.errors import InvalidId
from rest_framework import serializers
from rest_framework.fields import ListField, CharField
from rest_framework.reverse import reverse
from rest_framework_mongoengine.serializers import DocumentSerializer
from sensordatas.models import Sensordatas
from nodes.models import Nodes


class SensordataSerializer(DocumentSerializer):
    node = serializers.SlugRelatedField(slug_field="label", queryset=Nodes.objects)
    # extra field
    testing = serializers.BooleanField(required=False)
    url = serializers.SerializerMethodField()
    nodeurl = serializers.SerializerMethodField(method_name='getnodeurl')
    sensorurl = serializers.SerializerMethodField(method_name='getsensorurl')
    sensorlabel = serializers.SerializerMethodField(method_name='getsensorlabel')

    class Meta:
        model = Sensordatas
        fields = '__all__'

    def get_url(self, obj):
        return reverse('sensordata-detail', args=[obj.id], request=self.context['request'])

    def getnodeurl(self, obj):
        return reverse('nodes-detail', args=[obj.node.pk], request=self.context['request'])

    def getsensorurl(self, obj):
        return reverse('node-sensor-detail', args=[obj.node.pk, str(obj.sensor)], request=self.context['request'])

    @staticmethod
    def getsensorlabel(obj):
        obj.node.sensors.get(id=obj.sensor)
        return obj.node.sensors.get(id=obj.sensor).label

    def validate(self, data):
        super(SensordataSerializer, self).validate(data)
        node = data.get('node')

        ''' -1 means node has not pubcription limit '''
        if -1 is node.pubsperday:
            return data

        ''' check if node has remaining pubcription this day '''
        if 0 != node.pubsperdayremain:
            return data
        raise serializers.ValidationError('pubcription is limit.')

    def create(self, validated_data):
        node = validated_data.get('node')
        sensor = validated_data.get('sensor')

        ''' create new pubcription instance '''
        pub = Sensordatas()
        pub.node = node
        pub.sensor = sensor
        pub.data = validated_data.get('data')
        if not validated_data.get('testing'):
            pub.save()
        return pub


class SensordataFormatSerializer(DocumentSerializer):
    id = CharField()
    label = CharField()
    nodes = ListField()
    testing = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Sensordatas
        fields = ('id', 'label', 'nodes', 'testing')

    @staticmethod
    def is_objectid_valid(oid):
        try:
            ObjectId(oid)
            return True
        except (InvalidId, TypeError):
            return False

    @staticmethod
    def get_node(supenodeid, nodeid):
        try:
            return Nodes.objects.get(supernode=supenodeid, id=nodeid)
        except Nodes.DoesNotExist:
            return False

    @staticmethod
    def get_node_sensor(nodesensors, sensorlabel):
        try:
            return nodesensors.get(label=sensorlabel)
        except Exception:
            return False

    def validate(self, attrs):
        super(SensordataFormatSerializer, self).validate(attrs=attrs)
        supernode = self.context.get('request').user
        node = Nodes()
        errors = OrderedDict()
        nodeiderror = []
        nodeformaterror = []
        nodesensorerror = []

        '''validate format of node[i]'''
        for index, nodes in enumerate(attrs.get('nodes')):
            if not nodes.get('id'):
                nodeiderror.append(
                    "node[%d].id: This field may not be null." % index
                )
            else:
                if not self.is_objectid_valid(nodes.get('id')):
                    nodeiderror.append(
                        "node[%d].id: %s is not valid ObjectId." % (index, nodes.get('id'))
                    )
                else:
                    node = self.get_node(supernode.id, nodes.get('id'))
                    if not node:
                        nodeiderror.append(
                            "node[%d].id: Object with label=%s does not exist.." % (index, nodes.get('id'))
                        )
                        continue

            if not nodes.get('format'):
                nodeformaterror.append(
                    "node[%d].format: This field may not be null." % index
                )
            else:
                if not isinstance(nodes.get('format'), list):
                    nodeformaterror.append(
                        "node[%d].format: Expected a list." % index
                    )
                else:
                    if 2 != len(nodes.get('format')) or \
                            ('data' != nodes.get('format')[0] or 'timestamp' != nodes.get('format')[1]):
                        nodeformaterror.append(
                            "node[%d].format: Expected format ['data', 'timestamp']." % index
                        )

            if not nodes.get('sensors'):
                nodesensorerror.append(
                    "node[%d].sensors: This field may not be null." % index
                )
            else:
                if not isinstance(nodes.get('sensors'), list):
                    nodesensorerror.append(
                        "node[%d].sensors: Expected a list." % index
                    )
                else:
                    sensorerror = self.nodes_sensors_validate(index, node, nodes.get('sensors'))
                    if sensorerror:
                        nodesensorerror.append(sensorerror)
        else:
            if nodeiderror:
                errors['node'] = {'id': nodeiderror}
            if nodeformaterror:
                errors['node'] = {'format': nodeformaterror}
            if nodesensorerror:
                errors['node'] = {'sensors': nodesensorerror}

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    '''
    helper method: validate format of node[i].sensors
    '''
    def nodes_sensors_validate(self, index, node, sensors):
        sensorerror = []
        for jindex, sensor in enumerate(sensors):
            if not isinstance(sensor, dict):
                sensorerror.append(
                    "node[%d].sensors[%d]: Expected a dict." % (index, jindex)
                )

            if not sensor.get('label'):
                sensorerror.append(
                    "node[%d].sensors[%d].label: This field may not be null." % (index, jindex)
                )
            else:
                if not self.get_node_sensor(node.sensors, sensor.get('label')):
                    sensorerror.append(
                        "node[%d].sensors[%d].label: Object with label=%s does not exist.."
                        % (index, jindex, sensor.get('label'))
                    )

            if not sensor.get('value'):
                sensorerror.append(
                    "node[%d].sensors[%d].value: This field may not be null." % (index, jindex)
                )
            else:
                if not isinstance(sensor.get('value'), list):
                    sensorerror.append(
                        "node[%d].sensors[%d].value: Expected a list of int." %
                        (index, jindex)
                    )
                else:
                    for kindex, values in enumerate(sensor.get('value')):
                        if not isinstance(values[0], int) or not isinstance(values[1], int):
                            sensorerror.append(
                                "node[%d].sensors[%d].value[%d]: Expected list of int." %
                                (index, jindex, kindex)
                            )
        if sensorerror:
            return sensorerror
        else:
            return None

    def create(self, validated_data):
        supernode = self.context.get('request').user
        nodes = validated_data.get('nodes')
        istesting = validated_data.get('testing')
        count = 0

        for node in nodes:
            node_obj = self.get_node(supernode.id, node.get('id'))
            for sensor in node.get('sensors'):
                sensor_obj = node_obj.sensors.get(label=sensor.get('label'))
                for value in sensor.get('value'):
                    data = {'node': node_obj.label, 'sensor': sensor_obj.id,
                            'data': value[0], 'testing': istesting}
                    serializer = SensordataSerializer(data=data)
                    if serializer.is_valid():
                        count += 1
                        serializer.save()
                    else:
                        raise serializers.ValidationError(serializer.errors)
                if not istesting:
                    ''' decrement Nodes pubsperdayremain when node has publish limit '''
                    if -1 is not node_obj.pubsperday:
                        node_obj.pubsperdayremain -= 1
                        node_obj.save()
        return "%d sensordatas has successfully added." % count
