from django.db import models
from core.utils import generate_custom_id

class Group(models.Model):
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    name = models.CharField(max_length=150, verbose_name="Guruh nomi")
    image = models.ImageField(upload_to='groups/', null=True, blank=True, verbose_name="Rasm")
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.kindergarten.name}"


class Camera(models.Model):
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    kamera_nomi = models.CharField(max_length=150, verbose_name="Kamera nomi")
    kamera_url = models.URLField(max_length=500, verbose_name="Kamera URL manzili")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='cameras', null=True, blank=True)
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='cameras')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.kamera_nomi} - {self.kindergarten.name}"
