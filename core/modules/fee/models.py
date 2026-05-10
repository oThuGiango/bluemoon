from django.db import models
from core.modules.account.models import TaiKhoan
from core.modules.base.models import DonViTinh, TrangThaiDotThu


class KhoanThu(models.Model):
    id_khoanthu = models.AutoField(primary_key=True)
    ten_khoanthu = models.CharField(max_length=100)
    don_gia = models.DecimalField(max_digits=15, decimal_places=2)
    don_vi_tinh = models.CharField(
        max_length=20,
        choices=DonViTinh.choices,
        default=DonViTinh.NGUOI,
    )
    phi_bat_buoc = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = True
        db_table = "khoanthu"

    def __str__(self):
        return self.ten_khoanthu


class DotThuPhi(models.Model):
    id_dotthu = models.AutoField(primary_key=True)
    ten_dotthu = models.CharField(max_length=250)
    ngay_batdau = models.DateField()
    ngay_ketthuc = models.DateField(null=True, blank=True)
    LOAI_DOT_THU_CHOICES = [
        ("dinh_ky", "Định kỳ"),
        ("bo_sung", "Bổ sung"),
        ("tu_nguyen", "Tự nguyện"),
        ("khac", "Khác"),
    ]
    loai_dot_thu = models.CharField(
        max_length=20,
        choices=LOAI_DOT_THU_CHOICES,
        default="dinh_ky",
    )
    trang_thai = models.CharField(
        max_length=6,
        choices=TrangThaiDotThu.choices,
        default=TrangThaiDotThu.OPEN,
    )
    id_khoanthu = models.ManyToManyField(
        "core.KhoanThu",
        db_table="dotthuphi_khoanthu",
        related_name="dot_thuphi",
        blank=True,
    )
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = True
        db_table = "dotthuphi"

    def __str__(self):
        return self.ten_dotthu


class HoaDon(models.Model):
    id_hoadon = models.AutoField(primary_key=True)
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2)
    ngay_nop = models.DateField(null=True, blank=True)
    id_dotthu = models.ForeignKey(
        "core.DotThuPhi",
        on_delete=models.RESTRICT,
        db_column="id_dotthu",
        related_name="hoa_dons",
        default=1,
    )
    id_hokhau = models.ForeignKey(
        "core.HoKhau",
        on_delete=models.RESTRICT,
        db_column="id_hokhau",
        related_name="hoa_dons",
        default=1,
    )
    da_dong = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    
    CHANNEL_CHOICES = [
        ("tien_mat", "Tiền mặt"),
        ("chuyen_khoan", "Chuyển khoản"),
        ("khac", "Khác"),
    ]
    channel = models.CharField(
        max_length=20, choices=CHANNEL_CHOICES, default="tien_mat")

    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = True
        db_table = "hoadon"
        constraints = [
            models.UniqueConstraint(
                fields=["id_hokhau", "id_dotthu"], name="uq_hoadon_hokhau_dotthu"),
        ]
        indexes = [
            models.Index(fields=["id_hokhau"], name="idx_hoadon_hokhau"),
            models.Index(fields=["id_dotthu"], name="idx_hoadon_dotthu"),
        ]


class HoaDonChiTiet(models.Model):
    id = models.AutoField(primary_key=True)
    hoadon = models.ForeignKey(
        "core.HoaDon",
        on_delete=models.CASCADE,
        db_column="id_hoadon",
        related_name="chi_tiets",
    )
    khoanthu = models.ForeignKey(
        "core.KhoanThu",
        on_delete=models.RESTRICT,
        db_column="id_khoanthu",
        related_name="chitiet_hoadons",
    )
    so_luong = models.DecimalField(max_digits=10, decimal_places=2)
    thanh_tien = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        managed = True
        db_table = "hoadon_chitiet"

    def __str__(self):
        return f"HDCT #{self.id_chitiet} - HD:{self.hoadon_id} - KT:{self.khoanthu_id}"
