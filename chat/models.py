from django.db import models
from django.utils import timezone
from core.utils import generate_custom_id

class Chat(models.Model):
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    group = models.OneToOneField('groups.Group', on_delete=models.CASCADE, related_name='chat', verbose_name="Guruh")
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='chats', verbose_name="Bog'cha")
    name = models.CharField(max_length=150, verbose_name="Chat nomi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Guruh chati"
        verbose_name_plural = "Guruh chatlari"

    def __str__(self):
        return f"{self.name} ({self.kindergarten.name})"


class ChatMember(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Direktor/Admin'
        STAFF = 'staff', 'Xodim'
        PARENT = 'parent', 'Ota-ona'

    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='members', verbose_name="Chat")
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='chat_memberships', verbose_name="Foydalanuvchi")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARENT, verbose_name="Rol")
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now, verbose_name="Oxirgi ko'rgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        unique_together = ('chat', 'user')
        verbose_name = "Chat a'zosi"
        verbose_name_plural = "Chat a'zolari"

    def __str__(self):
        return f"{self.user.username} - {self.chat.name} ({self.get_role_display()})"


class Message(models.Model):
    class MessageType(models.TextChoices):
        TEXT = 'text', 'Matn'
        IMAGE = 'image', 'Rasm'
        FILE = 'file', 'Fayl'
        VOICE = 'voice', 'Ovozli xabar'

    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name="Chat")
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Yuboruvchi")
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT, verbose_name="Xabar turi")
    text = models.TextField(blank=True, null=True, verbose_name="Matn")
    media = models.FileField(upload_to='chat/media/%Y/%m/', blank=True, null=True, verbose_name="Media fayl")
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies', verbose_name="Javob")
    is_deleted = models.BooleanField(default=False, verbose_name="O'chirilgan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"

    def __str__(self):
        return f"{self.sender.username}: {self.text[:20] if self.text else self.message_type}"


class MessageReadStatus(models.Model):
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses', verbose_name="Xabar")
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='read_messages', verbose_name="Foydalanuvchi")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')
        verbose_name = "Xabar o'qish holati"
        verbose_name_plural = "Xabar o'qish holatlari"

    def __str__(self):
        return f"{self.user.username} o'qidi: {self.message.id}"
