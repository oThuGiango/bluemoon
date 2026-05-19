from django.db import models
from django.conf import settings


class ThongBao(models.Model):
    NGUOI_NHAN_CHOICES = [
        ("ketoan", "Kế toán"),
        ("cudan", "Cư dân"),
        ("all", "Tất cả"),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="thongbao_gui")
    doi_tuong = models.CharField(
        max_length=10, choices=NGUOI_NHAN_CHOICES)
  
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"
