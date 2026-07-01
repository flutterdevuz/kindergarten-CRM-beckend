from django.db import models
from django.utils import timezone
from core.utils import generate_custom_id

class ChildAttendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Keldi'),
        ('absent', 'Kelmadi'),
        ('late', 'Kechikdi'),
        ('sick', 'Kasal'),
    )

    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=64, editable=False)
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='attendances')
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='attendances')
    kindergarten = models.ForeignKey('core.Kindergarten', on_delete=models.CASCADE, related_name='attendances')
    
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    
    # Face ID va avtomat tizimlar uchun qo'shimcha maydonlar
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    
    recorded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        # Bir kunda bitta bola uchun faqat bitta davomat bo'lishi kerak
        unique_together = ('child', 'date')

    def __str__(self):
        return f"{self.child.name} - {self.date} ({self.status})"
