from django.contrib.auth.models import AbstractUser
from django.db import models
from core.utils import generate_custom_id

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Bog\'cha Admini'
        STAFF = 'staff', 'Xodim'
        PARENT = 'parent', 'Ota-ona'
        SUPERADMIN = 'superadmin', 'Tizim Admini'

    # Overriding the id field to use our custom generated unique string primary key
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    
    # We will expand this model in subsequent tasks
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARENT)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class KindergartenRole(models.Model):
    """Bog'cha ichidagi xodimlar rollari (Tarbiyachi, Qorovul, Oshpaz)"""
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    name = models.CharField(max_length=150, verbose_name="Rol nomi")
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return f"{self.name} - {self.kindergarten.name}"


class StaffProfile(models.Model):
    """Xodimlar profili (bitta xodim faqat bitta bog'chaga tegishli bo'ladi)"""
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='staff')
    
    name = models.CharField(max_length=150, verbose_name="Ismi", blank=True, null=True)
    surname = models.CharField(max_length=150, verbose_name="Familiyasi", blank=True, null=True)
    birth_day = models.DateField(null=True, blank=True)
    passport_id = models.CharField(max_length=50, blank=True, null=True)
    passport_seria = models.CharField(max_length=50, blank=True, null=True)
    
    image = models.ImageField(upload_to='staff/images/', null=True, blank=True)
    camera_image = models.ImageField(upload_to='staff/camera/', null=True, blank=True)
    
    role = models.ForeignKey(KindergartenRole, on_delete=models.SET_NULL, null=True, related_name='staff_profiles')
    groups = models.ManyToManyField('groups.Group', related_name='staff_profiles', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name or self.user.username} - {self.kindergarten.name}"


class ParentProfile(models.Model):
    """Ota-onalar profili (bitta ota-ona profili bitta bog'cha uchun)"""
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='parents')
    
    name = models.CharField(max_length=150, verbose_name="Ismi", blank=True, null=True)
    surname = models.CharField(max_length=150, verbose_name="Familiyasi", blank=True, null=True)
    passport_id = models.CharField(max_length=50, blank=True, null=True)
    passport_seria = models.CharField(max_length=50, blank=True, null=True)
    birth_day = models.DateField(null=True, blank=True)
    
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, related_name='parent_profiles')
    child = models.ForeignKey('children.Child', on_delete=models.SET_NULL, null=True, related_name='parent_profiles')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name or self.user.username} - {self.kindergarten.name}"


class KindergartenAdminProfile(models.Model):
    """Bog'cha direktori/admini profili"""
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='admins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.kindergarten.name}"
