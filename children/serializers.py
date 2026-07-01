from rest_framework import serializers
from .models import Child

class ChildSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Child
        fields = [
            'id', 'name', 'surname', 'image', 'camera_image',
            'metrka_id', 'metrka_seria', 'birth_day', 'kasallik_tarixi',
            'group', 'group_name', 'kindergarten', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'kindergarten', 'group_name']

    def get_group_name(self, obj):
        return obj.group.name if obj.group else None
