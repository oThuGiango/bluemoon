from django.db import models

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

    class Meta:
        managed = True
        db_table = "khoanthu"

    def __str__(self):
        return self.ten_khoanthu


class DotThuPhi(models.Model):
    id_dotthu = models.IntegerField(primary_key=True)
    ten_dotthu = models.CharField(max_length=100)
    ngay_batdau = models.DateField()
    ngay_ketthuc = models.DateField(null=True, blank=True)
    trang_thai = models.CharField(
        max_length=6,
        choices=TrangThaiDotThu.choices,
        default=TrangThaiDotThu.OPEN,
    )
    id_khoanthu = models.ForeignKey(
        "core.KhoanThu",
        on_delete=models.RESTRICT,
        db_column="id_khoanthu",
        related_name="dot_thuphi",
        default=1,
    )

    class Meta:
        managed = True
        db_table = "dotthuphi"
        indexes = [
            models.Index(fields=["id_khoanthu"], name="idx_dotthu_khoanthu"),
        ]

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
