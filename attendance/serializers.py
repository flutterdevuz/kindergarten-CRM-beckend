from rest_framework import serializers
from .models import ChildAttendance

class ChildAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildAttendance
        fields = ['id', 'child', 'group', 'kindergarten', 'date', 'status', 'time_in', 'time_out', 'recorded_by', 'created_at']
        read_only_fields = ['id', 'kindergarten', 'recorded_by', 'created_at']

class BulkAttendanceSerializer(serializers.Serializer):
    group_id = serializers.CharField()
    date = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField()
    )
    # records formati: [{"child_id": "...", "status": "present", "time_in": "..."}, ...]
