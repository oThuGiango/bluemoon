from django.db import models
from django.db.models import Q, UniqueConstraint
from core.modules.apartment.models import CanHo
from core.modules.base.models import LoaiBienDong
from core.modules.account.models import TaiKhoan
from django.core.validators import RegexValidator


class HoKhau(models.Model):
    id_hokhau = models.AutoField(primary_key=True)
    id_canho = models.ForeignKey(
        CanHo,
        on_delete=models.RESTRICT,
        db_column="id_canho",
        related_name="can_ho",
    )
    id_chuho = models.ForeignKey(
        TaiKhoan,
        on_delete=models.RESTRICT,
        db_column="id_chuho",
        related_name="chu_ho",
    )
    RESIDENT_STT_CHOICES = [
        ("thuong_tru", "Thường trú"),
        ("tam_tru", "Tạm trú"),
        ("tam_vang", "Tạm vắng"),
        ("khac", "Khác"),
    ]
    resident_status = models.CharField(
        max_length=20,
        choices=RESIDENT_STT_CHOICES,
        default="tam_vang",
        verbose_name="Tình trạng cư trú"
    )
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Tự động cập nhật status của căn hộ khi HoKhau thay đổi
        if self.id_canho:
            # Nếu có hộ khẩu active, chưa xóa, cập nhật status căn hộ
            active_hokhau = HoKhau.objects.filter(
                id_canho=self.id_canho, is_deleted=False, is_active=True).first()
            if active_hokhau and active_hokhau.resident_status:
                if active_hokhau.resident_status in ["thuong_tru", "tam_vang"]:
                    self.id_canho.status = "dang_o"
                elif active_hokhau.resident_status == "tam_tru":
                    self.id_canho.status = "cho_thue"
                else:
                    self.id_canho.status = "khac"
            else:
                self.id_canho.status = "de_trong"
            self.id_canho.save(update_fields=["status"])

    class Meta:
        db_table = "hokhau"
        constraints = [
            UniqueConstraint(
                fields=["id_canho", "id_chuho"],
                condition=Q(is_deleted=False),
                name="unique_canho_chuho_not_deleted"
            )
        ]

    def __str__(self):
        return self.id_canho.so_can_ho


class NhanKhau(models.Model):
    id_nhankhau = models.AutoField(primary_key=True)
    ho_ten = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ("M", "Nam"),
        ("F", "Nữ"),
        ("O", "Khác"),
    ]
    gioi_tinh = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default="O")
    ngay_sinh = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    cccd = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\d{12}$', message='CCCD phải gồm 12 chữ số.')]
    )
    so_dien_thoai = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^0\d{9}$', message='Số điện thoại phải bắt đầu bằng 0 và gồm 10 chữ số.')]
    )
    email = models.EmailField(max_length=254, null=True, blank=True)
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

    def save(self, *args, **kwargs):
        # Tự động set is_chu_ho nếu quan hệ là chủ hộ
        self.is_chu_ho = self.quan_he_chu_ho == 'chu_ho'

        super().save(*args, **kwargs)


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
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "biendongnhankhau"
