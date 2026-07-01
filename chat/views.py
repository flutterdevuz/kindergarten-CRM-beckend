from rest_framework import views, generics, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from chat.models import Chat, ChatMember, Message, MessageReadStatus
from chat.serializers import ChatSerializer, ChatMemberSerializer, MessageSerializer

class IsChatMember(permissions.BasePermission):
    """
    Faqatgina faol chat a'zolari uchun ruxsat berish
    """
    def has_permission(self, request, view):
        chat_id = view.kwargs.get('chat_id')
        if not chat_id:
            return True
        return ChatMember.objects.filter(chat_id=chat_id, user=request.user, is_active=True).exists()


class ChatListAPIView(generics.ListAPIView):
    """
    Foydalanuvchi a'zo bo'lgan barcha faol chatlar ro'yxati
    """
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # User is active member in the chat
        active_chat_ids = ChatMember.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('chat_id', flat=True)
        
        return Chat.objects.filter(id__in=active_chat_ids)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ChatMessagesAPIView(generics.ListAPIView):
    """
    Chatdagi barcha xabarlar ro'yxati.
    Parametrlar:
    - after_id: Shu ID dan keyingi kelgan xabarlarni olish (polling uchun qulay)
    - limit: Nechta xabar qaytarish kerakligi (default: 50)
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatMember]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        queryset = Message.objects.filter(chat_id=chat_id)
        
        after_id = self.request.query_params.get('after_id')
        if after_id:
            try:
                after_msg = Message.objects.get(id=after_id, chat_id=chat_id)
                queryset = queryset.filter(created_at__gt=after_msg.created_at)
            except Message.DoesNotExist:
                pass
                
        return queryset.order_by('created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Polling/Normal fetch limit
        limit = request.query_params.get('limit')
        if limit:
            try:
                limit = int(limit)
                # Get the latest 'limit' messages, but in correct chronological order
                # So we take the last 'limit' items from chronological queryset
                count = queryset.count()
                if count > limit:
                    queryset = queryset[count - limit:]
            except ValueError:
                pass
        else:
            # Default to last 50 messages if no pagination / after_id
            if not request.query_params.get('after_id'):
                count = queryset.count()
                if count > 50:
                    queryset = queryset[count - 50:]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SendMessageAPIView(views.APIView):
    """
    Chatga xabar yuborish.
    Fields: message_type (text/image/file/voice), text, media, reply_to
    """
    permission_classes = [permissions.IsAuthenticated, IsChatMember]

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        
        message_type = request.data.get('message_type', Message.MessageType.TEXT)
        text = request.data.get('text', '')
        media = request.FILES.get('media') or request.data.get('media')
        reply_to_id = request.data.get('reply_to')

        if message_type not in Message.MessageType.values:
            return Response(
                {"error": f"Noto'g'ri xabar turi. Quyidagilardan biri bo'lishi kerak: {Message.MessageType.values}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if message_type == Message.MessageType.TEXT and not text.strip():
            return Response(
                {"error": "Matnli xabar uchun text maydoni bo'sh bo'lishi mumkin emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if message_type in [Message.MessageType.IMAGE, Message.MessageType.FILE, Message.MessageType.VOICE] and not media:
            return Response(
                {"error": "Ushbu xabar turi uchun media fayl yuklanishi shart."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reply_to = None
        if reply_to_id:
            reply_to = get_object_or_404(Message, id=reply_to_id, chat=chat)

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            message_type=message_type,
            text=text.strip() if text else None,
            media=media if media else None,
            reply_to=reply_to
        )

        # Update sender's last_seen in this chat
        ChatMember.objects.filter(chat=chat, user=request.user).update(last_seen=timezone.now())

        # Automatically mark as read for the sender
        MessageReadStatus.objects.get_or_create(message=message, user=request.user)

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkChatAsReadAPIView(views.APIView):
    """
    Chatdagi barcha o'qilmagan xabarlarni o'qilgan deb belgilash
    """
    permission_classes = [permissions.IsAuthenticated, IsChatMember]

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        member = get_object_or_404(ChatMember, chat=chat, user=request.user, is_active=True)

        # Mark all messages in chat as read
        unread_messages = Message.objects.filter(
            chat=chat,
            created_at__gt=member.last_seen
        ).exclude(sender=request.user)

        # Create read status for each
        for msg in unread_messages:
            MessageReadStatus.objects.get_or_create(message=msg, user=request.user)

        # Update last_seen
        member.last_seen = timezone.now()
        member.save()

        return Response({"success": True, "message": "Barcha xabarlar o'qildi deb belgilandi."})


class ChatMembersAPIView(generics.ListAPIView):
    """
    Chatdagi faol a'zolar ro'yxati
    """
    serializer_class = ChatMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatMember]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        return ChatMember.objects.filter(chat_id=chat_id, is_active=True)


class ChatUnreadCountAPIView(views.APIView):
    """
    Ushbu chatdagi o'qilmagan xabarlar sonini olish
    """
    permission_classes = [permissions.IsAuthenticated, IsChatMember]

    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        member = get_object_or_404(ChatMember, chat=chat, user=request.user, is_active=True)

        unread_count = Message.objects.filter(
            chat=chat,
            created_at__gt=member.last_seen
        ).exclude(sender=request.user).count()

        return Response({"chat_id": chat_id, "unread_count": unread_count})


class DeleteMessageAPIView(views.APIView):
    """
    Xabarni o'chirish (soft delete).
    Faqat xabar yuboruvchisi yoki chat/bog'cha admini o'chira oladi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        
        # Check permissions: sender, or chat admin
        is_sender = (message.sender == request.user)
        
        is_admin = False
        try:
            member = ChatMember.objects.get(chat=message.chat, user=request.user, is_active=True)
            if member.role == ChatMember.Role.ADMIN:
                is_admin = True
        except ChatMember.DoesNotExist:
            pass

        # Also django superuser is admin
        if request.user.is_superuser or request.user.role == 'admin':
            is_admin = True

        if not (is_sender or is_admin):
            return Response(
                {"error": "Sizda ushbu xabarni o'chirish huquqi yo'q."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Soft delete
        message.is_deleted = True
        message.text = None
        if message.media:
            # Delete media file from storage if wanted, or just clean reference
            message.media.delete(save=False)
            message.media = None
        message.save()

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
