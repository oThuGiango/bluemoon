# backend/models.py
from django.db import models
from django.contrib.postgres.fields import CITextField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager



class TaiKhoanManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username là bắt buộc")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)   # ✅ hash chuẩn Django
        user.save()
        return user
    

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, password, **extra_fields)




# ===== ENUM choices (map PostgreSQL ENUM sang Python choices) =====
class LoaiBienDong(models.TextChoices):
    TAM_TRU = 'tam_tru', 'Tạm trú'
    TAM_VANG = 'tam_vang', 'Tạm vắng'
    THUONG_TRU = 'thuong_tru', 'Thường trú'

class DonViTinh(models.TextChoices):
    NGUOI = 'nguoi', 'Người'
    HO = 'ho', 'Hộ gia đình'
    THANG = 'thang', 'Tháng'
    NAM = 'nam', 'Năm'
    LUOT = 'luot', 'Lượt'
    
class TrangThaiDotThu(models.TextChoices):
    OPEN = 'open', 'Mở'
    CLOSED = 'closed', 'Đóng'

# ===== 1) VaiTro =====
class VaiTro(models.Model):
    # SỬA: Dùng AutoField để ID tự tăng (1, 2, 3...)
    id_vaitro = models.AutoField(primary_key=True)
    ten_vaitro = models.CharField(max_length=50)
    class Meta:
        managed = True
        db_table = 'vaitro'

    def __str__(self):
        return self.ten_vaitro
# =======================
# Bảng Hộ khẩu
# =======================
class HoKhau(models.Model):
    id_hokhau = models.AutoField(primary_key=True)
    so_can_ho = models.CharField(max_length=20)
    dien_tich = models.FloatField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'hokhau'


# ===== 4) NhanKhau =====
class NhanKhau(models.Model):
    id_nhankhau = models.AutoField(primary_key=True) # SỬA
    ho_ten = models.CharField(max_length=100)
    ngay_sinh = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    cccd = models.CharField(max_length=12, unique=True, null=True, blank=True)
    quan_he_chu_ho = models.CharField(max_length=50, null=True, blank=True)
    id_hokhau = models.ForeignKey(
        HoKhau, on_delete=models.RESTRICT, db_column='id_hokhau', related_name='ho_khau', default=1
    )

    class Meta:
        managed = True
        db_table = 'nhankhau'
        indexes = [
            models.Index(fields=['id_hokhau'], name='id_hokhau'),
        ]

    def __str__(self):
        return self.ho_ten

# ===== 5) BienDongNhanKhau =====
class BienDongNhanKhau(models.Model):
    id_biendong = models.AutoField(primary_key=True) 
    loai_biendong = models.CharField(max_length=12, choices=LoaiBienDong.choices)
    ngay_batdau = models.DateField()
    ngay_ketthuc = models.DateField(null=True, blank=True)
    ly_do = models.TextField(null=True, blank=True)
    id_nhankhau = models.ForeignKey(
        NhanKhau, on_delete=models.CASCADE, db_column='id_nhankhau', related_name='nhankhau',
        default=1
    )
    class Meta:
            managed = True
            db_table = 'biendongnhankhau'

# =======================
# Bảng Tài khoản
# =======================
class TaiKhoan(AbstractBaseUser, PermissionsMixin):
    id_taikhoan = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)  # CITEXT có thể bỏ qua
    vaitro = models.ForeignKey(VaiTro, on_delete=models.SET_NULL,
        null=True,          # ✅ cho phép null
        blank=True, related_name='vaitro', db_column='id_vaitro')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)   # 🔥 BẮT BUỘC

    objects = TaiKhoanManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'taikhoan'   

# ===== 6) KhoanThu =====
class KhoanThu(models.Model):
    id_khoanthu = models.IntegerField(primary_key=True) 
    ten_khoanthu = models.CharField(max_length=100)
    don_gia = models.DecimalField(max_digits=15, decimal_places=2)
    don_vi_tinh = models.CharField(
        max_length=20,
        choices = DonViTinh.choices,
        default= DonViTinh.NGUOI
        )

    class Meta:
        managed = True
        db_table = 'khoanthu'

    def __str__(self):
        return self.ten_khoanthu

# ===== 7) DotThuPhi =====
class DotThuPhi(models.Model):
    id_dotthu = models.IntegerField(primary_key=True) 
    ten_dotthu = models.CharField(max_length=100)
    ngay_batdau = models.DateField()
    ngay_ketthuc = models.DateField(null=True, blank=True)
    trang_thai = models.CharField(
        max_length=6, 
        choices=TrangThaiDotThu.choices, 
        default=TrangThaiDotThu.OPEN
    )
    id_khoanthu = models.ForeignKey(
        'core.KhoanThu',            
        on_delete=models.RESTRICT,
        db_column='id_khoanthu',
        related_name='dot_thuphi',
        default=1
    )
    class Meta:
        managed = True
        db_table = 'dotthuphi'
        indexes = [
            models.Index(fields=['id_khoanthu'], name='idx_dotthu_khoanthu'),
        ]
    def __str__(self):
        return self.ten_dotthu

# ===== 8) HoaDon =====
class HoaDon (models.Model):
    id_hoadon = models.AutoField(primary_key=True) # SỬA
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2)
    ngay_nop = models.DateField(null=True, blank=True)
    id_dotthu = models.ForeignKey(
        'core.DotThuPhi',            
        on_delete=models.RESTRICT,
        db_column='id_dotthu',
        related_name='hoa_dons',
        default=1
    )
    id_hokhau = models.ForeignKey(
        'core.HoKhau',               
        on_delete=models.RESTRICT,
        db_column='id_hokhau',
        related_name='hoa_dons',
        default=1
    )

    class Meta:
        managed = True
        db_table = 'hoadon'
        constraints = [
            models.UniqueConstraint(fields=['id_hokhau', 'id_dotthu'], name='uq_hoadon_hokhau_dotthu'),
        ]
        indexes = [
            models.Index(fields=['id_hokhau'], name='idx_hoadon_hokhau'),
            models.Index(fields=['id_dotthu'], name='idx_hoadon_dotthu'),
        ]