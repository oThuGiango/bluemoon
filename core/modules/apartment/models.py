from django.db import models


class Building(models.Model):
    name = models.CharField(max_length=20, unique=True,
                            verbose_name="Tên tòa nhà")
    max_floor = models.PositiveIntegerField(verbose_name="Số tầng tối đa")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "building"


class CanHo(models.Model):
    id_canho = models.AutoField(primary_key=True)
    so_can_ho = models.CharField(max_length=20, verbose_name="Số căn hộ")
    dien_tich = models.FloatField(null=True, blank=True, verbose_name="Diện tích")
    floor = models.IntegerField(null=True, blank=True, verbose_name="Tầng")
    building = models.ForeignKey(
        Building,
        on_delete=models.RESTRICT,
        db_column="building_id",
        related_name="canhos",
        null=True,
        blank=True,
        verbose_name="Tòa nhà"
    )
    APARTMENT_TYPE_CHOICES = [
        ("studio", "Studio"),
        ("1pn", "1 Phòng ngủ"),
        ("2pn", "2 Phòng ngủ"),
        ("3pn", "3 Phòng ngủ"),
        ("khac", "Khác"),
    ]
    apartment_type = models.CharField(
        max_length=20, choices=APARTMENT_TYPE_CHOICES, null=True, blank=True, verbose_name="Loại căn hộ")
    STATUS_CHOICES = [
        ("dang_o", "Đang ở"),
        ("de_trong", "Để trống"),
        ("cho_thue", "Cho thuê"),
        ("khac", "Khác"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default="de_trong", verbose_name="Trạng thái sử dụng")
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "canho"
        
    def save(self, *args, **kwargs):
        if self.building and self.floor is not None:
            if self.floor > self.building.max_floor:
                self.floor = self.building.max_floor
        super().save(*args, **kwargs)
