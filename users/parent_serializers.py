from rest_framework import serializers
from .models import ParentProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class ParentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    username_display = serializers.SerializerMethodField(read_only=True)
    group_name = serializers.SerializerMethodField(read_only=True)
    child_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ParentProfile
        fields = [
            'id', 'username', 'username_display', 'password', 'name', 'surname',
            'passport_id', 'passport_seria', 'birth_day',
            'group', 'group_name', 'child', 'child_name',
            'kindergarten', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'kindergarten',
                            'username_display', 'group_name', 'child_name']

    def get_username_display(self, obj):
        return obj.user.username if obj.user else ''

    def get_group_name(self, obj):
        return obj.group.name if obj.group else None

    def get_child_name(self, obj):
        if obj.child:
            return f"{obj.child.name or ''} {obj.child.surname or ''}".strip()
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['username'] = instance.user.username if instance.user else ''
        return data

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password', None)

        if not password:
            raise serializers.ValidationError({'password': 'Parol kiritilishi shart'})

        user = User.objects.create_user(
            username=username,
            password=password,
            role=User.Role.PARENT
        )

        parent_profile = ParentProfile.objects.create(
            user=user,
            **validated_data
        )
        return parent_profile

    def update(self, instance, validated_data):
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)

        if username:
            instance.user.username = username
        if password:
            instance.user.set_password(password)
        if username or password:
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
