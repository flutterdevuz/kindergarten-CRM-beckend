from django.db import models
from core.utils import generate_custom_id

class Kindergarten(models.Model):
    """
    Tizimdagi asosiy ijarachi (tenant) obyekti. 
    Barcha xodimlar, bolalar va ota-onalar aynan bitta bog'chaga tegishli bo'ladi.
    """
    id = models.CharField(
        primary_key=True,
        default=generate_custom_id,
        max_length=64,
        editable=False,
    )
    name = models.CharField(max_length=150, verbose_name="Bog'cha nomi")
    is_active = models.BooleanField(default=True, verbose_name="Faol holatda")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bog'cha"
        verbose_name_plural = "Bog'chalar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class KindergartenApplication(models.Model):
    """
    Bog'cha ro'yxatdan o'tish arizasi.
    Website orqali kelgan arizalar shu yerda saqlanadi.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', '⏳ Kutilmoqda'
        ACTIVE = 'active', '✅ Faol'
        INACTIVE = 'inactive', '❌ Nofaol'

    id = models.CharField(
        primary_key=True,
        default=generate_custom_id,
        max_length=64,
        editable=False,
    )

    # Bog'cha ma'lumotlari
    name = models.CharField(
        max_length=150,
        verbose_name="Bog'cha nomi",
    )

    region = models.CharField(
        max_length=80,
        verbose_name="Viloyat",
    )

    district = models.CharField(
        max_length=80,
        verbose_name="Tuman / Shahar",
    )

    address = models.TextField(
        max_length=300,
        verbose_name="To'liq manzil",
        blank=True,
        default='',
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Telefon raqam",
    )

    # Holat
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Holat",
        db_index=True,
    )

    # Vaqtlar
    applied_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ariza vaqti",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Yangilangan",
    )

    class Meta:
        verbose_name = "Bog'cha arizasi"
        verbose_name_plural = "Bog'cha arizalari"
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.name} — {self.get_status_display()}"
