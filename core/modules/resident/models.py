from django.db import models

from core.modules.account.models import TaiKhoan
from core.modules.base.models import LoaiBienDong
from django.db.models import Q, UniqueConstraint

class HoKhau(models.Model):
    id_hokhau = models.AutoField(primary_key=True)
    so_can_ho = models.CharField(max_length=20)
    dien_tich = models.FloatField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "hokhau"


class NhanKhau(models.Model):
    id_nhankhau = models.AutoField(primary_key=True)
    ho_ten = models.CharField(max_length=100)
    ngay_sinh = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    cccd = models.CharField(max_length=12, unique=True, null=True, blank=True)
    QUAN_HE_CHOICES = [
        ("chu_ho", "Chủ hộ"),
        ("vo_chong", "Vợ/chồng"),
        ("cha_me", "Cha/mẹ"),
        ("anh_chi_em", "Anh/chị/em"),
        ("con", "Con"),
        ("ong_ba", "Ông/bà"),
        ("nguoi_giam_ho", "Người giám hộ"),
        ("o_thue_o_nho", "Ở thuê/ Ở nhờ"),
        ("khac", "Khác"),
    ]
    quan_he_chu_ho = models.CharField(
        max_length=20,
        choices=QUAN_HE_CHOICES,
        null=True,
        blank=True
    )
    is_chu_ho = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    id_hokhau = models.ForeignKey(
        HoKhau,
        on_delete=models.RESTRICT,
        db_column="id_hokhau",
        related_name="ho_khau",
        null=True,
        blank=True,)
    id_taikhoan = models.ForeignKey(
        TaiKhoan,
        on_delete=models.RESTRICT,
        db_column="id_taikhoan",
        related_name="acc_nhankhau",
        null=True,
        blank=True,
    )

    class Meta:
        managed = True
        db_table = "nhankhau"
        indexes = [
            models.Index(fields=["id_hokhau"], name="id_hokhau"),
        ]
        constraints = [
            UniqueConstraint(
                fields=['id_hokhau'],
                condition=Q(quan_he_chu_ho='chu_ho',
                            is_chu_ho=True, is_active=True),
                name='unique_active_chu_ho_per_hokhau'
            )
        ]

    def __str__(self):
        return self.ho_ten


class BienDongNhanKhau(models.Model):
    id_biendong = models.AutoField(primary_key=True)
    loai_biendong = models.CharField(
        max_length=12, choices=LoaiBienDong.choices)
    ngay_batdau = models.DateField()
    ngay_ketthuc = models.DateField(null=True, blank=True)
    ly_do = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    id_nhankhau = models.ForeignKey(
        NhanKhau,
        on_delete=models.CASCADE,
        db_column="id_nhankhau",
        related_name="nhan_khau",
        default=1,
    )

    class Meta:
        managed = True
        db_table = "biendongnhankhau"
