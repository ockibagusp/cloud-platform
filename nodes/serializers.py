from rest_framework import serializers
from nodes.models import Nodes


class NodeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    label = serializers.CharField(min_length=4, max_length=28)
    secretkey = serializers.CharField(max_length=16, write_only=True)
    subsperday = serializers.IntegerField(default=0)

    class Meta:
        model = Nodes
        fields = ('id', 'label', 'secretkey', 'subsperday')
