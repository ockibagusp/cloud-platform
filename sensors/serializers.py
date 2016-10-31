from rest_framework import serializers
from rest_framework.reverse import reverse
from nodes.models import Nodes
from sensors.models import Sensors


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    label = serializers.CharField(min_length=4, max_length=28)
    nodes = serializers.SlugRelatedField(slug_field="label", queryset=Nodes.objects)
    # extra field
    nodeurl = serializers.SerializerMethodField(method_name='getnodeurl')

    class Meta:
        model = Sensors
        fields = ('id', 'url', 'nodes', 'nodeurl', 'label',)

    def getnodeurl(self, obj):
        return reverse('nodes-detail', args=[obj.nodes.pk], request=self.context['request'])

    def create(self, validated_data):
        sensor = Sensors.objects.create(**validated_data)
        return sensor

    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.nodes = validated_data.get('nodes', instance.nodes)
        instance.save()
        return instance
