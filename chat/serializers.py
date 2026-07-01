from rest_framework import serializers
from django.contrib.auth import get_user_model
from chat.models import Chat, ChatMember, Message, MessageReadStatus

User = get_user_model()

def get_user_display_name(user):
    if user.role == 'staff' and hasattr(user, 'staff_profile'):
        profile = user.staff_profile
        if profile.name or profile.surname:
            return f"{profile.name or ''} {profile.surname or ''}".strip()
    elif user.role == 'parent' and hasattr(user, 'parent_profile'):
        profile = user.parent_profile
        if profile.name or profile.surname:
            return f"{profile.name or ''} {profile.surname or ''}".strip()
    return f"{user.first_name} {user.last_name}".strip() or user.username


class ChatMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = ChatMember
        fields = ['id', 'user', 'username', 'display_name', 'role', 'role_display', 'joined_at', 'last_seen', 'is_active']
        read_only_fields = ['id', 'user', 'joined_at', 'last_seen', 'is_active']

    def get_display_name(self, obj):
        return get_user_display_name(obj.user)


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    reply_to_info = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'chat', 'sender', 'sender_name', 'sender_role', 'sender_username',
            'message_type', 'text', 'media', 'reply_to', 'reply_to_info',
            'is_deleted', 'created_at', 'read_by'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'is_deleted', 'read_by']

    def get_sender_name(self, obj):
        return get_user_display_name(obj.sender)

    def get_reply_to_info(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'text': obj.reply_to.text if not obj.reply_to.is_deleted else "O'chirilgan xabar",
                'sender_name': get_user_display_name(obj.reply_to.sender),
                'message_type': obj.reply_to.message_type
            }
        return None

    def get_read_by(self, obj):
        statuses = MessageReadStatus.objects.filter(message=obj)
        return [
            {
                'user_id': status.user.id,
                'username': status.user.username,
                'display_name': get_user_display_name(status.user),
                'read_at': status.read_at
            }
            for status in statuses
        ]


class ChatSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'group', 'group_name', 'kindergarten', 'name', 'last_message', 'unread_count', 'created_at']
        read_only_fields = ['id', 'kindergarten', 'created_at']

    def get_last_message(self, obj):
        msg = Message.objects.filter(chat=obj).order_by('-created_at').first()
        if msg:
            return {
                'id': msg.id,
                'sender_name': get_user_display_name(msg.sender),
                'message_type': msg.message_type,
                'text': msg.text if not msg.is_deleted else "O'chirilgan xabar",
                'created_at': msg.created_at
            }
        return None

    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user:
            return 0
        try:
            member = ChatMember.objects.get(chat=obj, user=user)
            if not member.is_active:
                return 0
            # Unread messages: messages sent by others after the member's last_seen
            # and that haven't been marked read by this user
            return Message.objects.filter(
                chat=obj,
                created_at__gt=member.last_seen
            ).exclude(sender=user).count()
        except ChatMember.DoesNotExist:
            return 0
