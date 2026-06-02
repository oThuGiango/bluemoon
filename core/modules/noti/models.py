from django.db import models
from django.conf import settings
from core.modules.account.models import VaiTro


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


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("done", "Done"),
    ]
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="created_tickets", on_delete=models.CASCADE)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="assigned_tickets", on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=150, null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} (#{self.pk})"


class TicketResponse(models.Model):
    ticket = models.ForeignKey(
        Ticket, related_name="responses", on_delete=models.CASCADE)
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="ticket_responses", on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Response by {self.responder} on Ticket #{self.ticket_id}"
