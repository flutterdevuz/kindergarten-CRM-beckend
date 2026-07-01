from rest_framework import serializers
from .models import Group, Camera

class GroupSerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField(read_only=True)
    staff_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'image', 'children_count', 'staff_count', 'kindergarten', 'created_at']
        read_only_fields = ['id', 'kindergarten', 'created_at', 'children_count', 'staff_count']

    def get_children_count(self, obj):
        return obj.children.count()

    def get_staff_count(self, obj):
        return obj.staff_profiles.count()

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'kamera_nomi', 'kamera_url', 'group', 'kindergarten', 'created_at']
        read_only_fields = ['id', 'kindergarten', 'created_at']
