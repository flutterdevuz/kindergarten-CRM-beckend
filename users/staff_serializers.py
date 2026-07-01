from rest_framework import serializers
from .models import KindergartenRole, StaffProfile, User
from groups.models import Group

class KindergartenRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KindergartenRole
        fields = ['id', 'name', 'kindergarten']
        read_only_fields = ['id', 'kindergarten']


class StaffProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    groups = serializers.SerializerMethodField()
    group_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    role_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'name', 'surname', 'username', 'password', 'birth_day',
            'passport_id', 'passport_seria', 'groups', 'group_ids', 'image', 'camera_image',
            'role', 'role_name', 'kindergarten', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'kindergarten', 'created_at', 'updated_at']

    def get_groups(self, obj):
        return [{"id": g.id, "name": g.name} for g in obj.groups.all()]

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        groups_data = validated_data.pop('group_ids', [])
        role_name = validated_data.pop('role_name', None)
        
        # Username already exists check
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
            
        user = User.objects.create_user(
            username=username,
            password=password,
            role=User.Role.STAFF
        )
        
        # If role_name is provided, get or create the role for this kindergarten
        if role_name:
            kindergarten = self.context['request'].user.admin_profile.kindergarten
            role_obj, _ = KindergartenRole.objects.get_or_create(
                name=role_name,
                kindergarten=kindergarten
            )
            validated_data['role'] = role_obj

        staff_profile = StaffProfile.objects.create(user=user, **validated_data)
        if groups_data:
            staff_profile.groups.set(groups_data)
            
        return staff_profile

    def update(self, instance, validated_data):
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        groups_data = validated_data.pop('group_ids', None)
        role_name = validated_data.pop('role_name', None)

        if username:
            if User.objects.exclude(id=instance.user.id).filter(username=username).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})
            instance.user.username = username
        if password:
            instance.user.set_password(password)
        if username or password:
            instance.user.save()

        if role_name:
            kindergarten = instance.kindergarten
            role_obj, _ = KindergartenRole.objects.get_or_create(
                name=role_name,
                kindergarten=kindergarten
            )
            validated_data['role'] = role_obj

        if groups_data is not None:
            instance.groups.set(groups_data)

        return super().update(instance, validated_data)
