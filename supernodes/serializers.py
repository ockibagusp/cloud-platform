from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer
from users.models import User
from supernodes.models import Supernodes


class SuperNodesSerializer(DocumentSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects)
    # extra field
    url = serializers.HyperlinkedIdentityField(
        view_name='supernodes-detail',
        lookup_field='pk'
    )
    label = serializers.CharField(min_length=2, max_length=28)
    description = serializers.CharField(max_length=140, required=False)

    class Meta:
        model = Supernodes
        fields = '__all__'

    def validate_label(self, value):
        """
        rest_framework.validators.UniqueValidator can't handle label uniqueness
        if we just want to avoid the same label for a user and let it for other user instead.
        :param value: self.label
        :return: validated value
        """
        user = self.context.get('request').user
        supernode = Supernodes.objects.filter(user=user, label=value)

        # when updating instance
        if None is not self.instance:
            if not supernode or self.instance.label == value:
                return value
        elif not supernode:  # when create new instance
            return value
        raise serializers.ValidationError("This field must be unique.")

    def create(self, validated_data):
        supernode = Supernodes.objects.create(**validated_data)
        supernode.save()
        return supernode

    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
