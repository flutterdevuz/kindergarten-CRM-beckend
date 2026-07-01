from django.urls import path
from chat.views import (
    ChatListAPIView,
    ChatMessagesAPIView,
    SendMessageAPIView,
    MarkChatAsReadAPIView,
    ChatMembersAPIView,
    ChatUnreadCountAPIView,
    DeleteMessageAPIView
)

app_name = 'chat'

urlpatterns = [
    path('chat/list/', ChatListAPIView.as_view(), name='chat_list'),
    path('chat/<str:chat_id>/messages/', ChatMessagesAPIView.as_view(), name='chat_messages'),
    path('chat/<str:chat_id>/send/', SendMessageAPIView.as_view(), name='send_message'),
    path('chat/<str:chat_id>/read/', MarkChatAsReadAPIView.as_view(), name='mark_read'),
    path('chat/<str:chat_id>/members/', ChatMembersAPIView.as_view(), name='chat_members'),
    path('chat/<str:chat_id>/unread-count/', ChatUnreadCountAPIView.as_view(), name='unread_count'),
    path('chat/message/<str:message_id>/', DeleteMessageAPIView.as_view(), name='delete_message'),
]
