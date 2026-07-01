from django.contrib import admin
from chat.models import Chat, ChatMember, Message, MessageReadStatus

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'kindergarten', 'created_at')
    search_fields = ('name', 'group__name', 'kindergarten__name')
    list_filter = ('kindergarten', 'created_at')


@admin.register(ChatMember)
class ChatMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'role', 'joined_at', 'last_seen', 'is_active')
    search_fields = ('chat__name', 'user__username', 'user__first_name', 'user__last_name')
    list_filter = ('role', 'is_active', 'chat__kindergarten')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'message_type', 'is_deleted', 'created_at')
    search_fields = ('chat__name', 'sender__username', 'text')
    list_filter = ('message_type', 'is_deleted', 'created_at', 'chat__kindergarten')


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'read_at')
    search_fields = ('message__id', 'user__username')
    list_filter = ('read_at',)
