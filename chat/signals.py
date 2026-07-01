from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from groups.models import Group
from users.models import StaffProfile, ParentProfile, KindergartenAdminProfile
from chat.models import Chat, ChatMember

@receiver(post_save, sender=Group)
def create_group_chat(sender, instance, created, **kwargs):
    if created:
        chat, _ = Chat.objects.get_or_create(
            group=instance,
            kindergarten=instance.kindergarten,
            defaults={'name': instance.name}
        )
        # Add all kindergarten admins to the chat
        admins = KindergartenAdminProfile.objects.filter(kindergarten=instance.kindergarten)
        for admin in admins:
            ChatMember.objects.get_or_create(
                chat=chat,
                user=admin.user,
                defaults={'role': ChatMember.Role.ADMIN, 'is_active': True}
            )
    else:
        # Update chat name if group name changes
        Chat.objects.filter(group=instance).update(name=instance.name)


@receiver(post_save, sender=KindergartenAdminProfile)
def add_new_admin_to_chats(sender, instance, created, **kwargs):
    if created:
        # Add new admin to all chats of their kindergarten
        chats = Chat.objects.filter(kindergarten=instance.kindergarten)
        for chat in chats:
            ChatMember.objects.get_or_create(
                chat=chat,
                user=instance.user,
                defaults={'role': ChatMember.Role.ADMIN, 'is_active': True}
            )


@receiver(m2m_changed, sender=StaffProfile.groups.through)
def update_staff_chats(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Get currently assigned groups
        current_group_ids = instance.groups.values_list('id', flat=True)
        
        # Get chats for these groups
        chats = Chat.objects.filter(group__in=current_group_ids)
        chat_ids = list(chats.values_list('id', flat=True))
        
        # Deactivate all their memberships for chats of this kindergarten that are NOT in current groups
        other_chats = Chat.objects.filter(kindergarten=instance.kindergarten).exclude(id__in=chat_ids)
        ChatMember.objects.filter(user=instance.user, chat__in=other_chats).update(is_active=False)
        
        # Activate/Create memberships for current groups
        for chat in chats:
            member, created = ChatMember.objects.get_or_create(
                chat=chat,
                user=instance.user,
                defaults={'role': ChatMember.Role.STAFF, 'is_active': True}
            )
            if not created and (not member.is_active or member.role != ChatMember.Role.STAFF):
                member.is_active = True
                member.role = ChatMember.Role.STAFF
                member.save()


@receiver(post_save, sender=ParentProfile)
def update_parent_chats(sender, instance, created, **kwargs):
    if instance.group:
        try:
            chat = Chat.objects.get(group=instance.group)
            
            # Deactivate from all other chats of this kindergarten
            other_chats = Chat.objects.filter(kindergarten=instance.kindergarten).exclude(id=chat.id)
            ChatMember.objects.filter(user=instance.user, chat__in=other_chats).update(is_active=False)
            
            # Add/Activate in current chat
            member, created = ChatMember.objects.get_or_create(
                chat=chat,
                user=instance.user,
                defaults={'role': ChatMember.Role.PARENT, 'is_active': True}
            )
            if not created and (not member.is_active or member.role != ChatMember.Role.PARENT):
                member.is_active = True
                member.role = ChatMember.Role.PARENT
                member.save()
        except Chat.DoesNotExist:
            pass
    else:
        # If parent has no group, deactivate them from all chats of this kindergarten
        other_chats = Chat.objects.filter(kindergarten=instance.kindergarten)
        ChatMember.objects.filter(user=instance.user, chat__in=other_chats).update(is_active=False)
