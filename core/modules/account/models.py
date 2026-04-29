from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class TaiKhoanManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username là bắt buộc")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, password, **extra_fields)


class VaiTro(models.Model):
    id_vaitro = models.AutoField(primary_key=True)
    ten_vaitro = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = "vaitro"

    def __str__(self):
        return self.ten_vaitro


class TaiKhoan(AbstractBaseUser, PermissionsMixin):
    id_taikhoan = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    vaitro = models.ForeignKey(
        VaiTro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vaitro",
        db_column="id_vaitro",
    )

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    create_by = models.CharField(max_length=100, null=True, blank=True)

    objects = TaiKhoanManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "taikhoan"
