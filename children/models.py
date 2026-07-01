from django.db import models
from core.utils import generate_custom_id

class Child(models.Model):
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    name = models.CharField(max_length=150, verbose_name="Ismi")
    surname = models.CharField(max_length=150, verbose_name="Familiyasi")
    image = models.ImageField(upload_to='children/images/', null=True, blank=True)
    camera_image = models.ImageField(upload_to='children/camera/', null=True, blank=True)
    
    metrka_id = models.CharField(max_length=50, blank=True, null=True)
    metrka_seria = models.CharField(max_length=50, blank=True, null=True)
    birth_day = models.DateField(null=True, blank=True)
    
    # {"id":"string", "name":"nomi"} formatdagi ro'yxat
    kasallik_tarixi = models.JSONField(default=list, blank=True)
    
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, related_name='children')
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='children')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # uploaded_at o'rniga

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} {self.surname}"
