from django.db import models


class LoaiBienDong(models.TextChoices):
    TAM_TRU = "tam_tru", "Tạm trú"
    TAM_VANG = "tam_vang", "Tạm vắng"
    THUONG_TRU = "thuong_tru", "Thường trú"
    CHAM_DUT = "cham_dut", "Chấm dứt cư trú"


class DonViTinh(models.TextChoices):
    NGUOI = "nguoi", "Người"
    HO = "ho", "Hộ gia đình"
    THANG = "thang", "Tháng"
    NAM = "nam", "Năm"
    LUOT = "luot", "Lượt"
    DIENTICH = "dientich", "Diện tích (m2)"


class TrangThaiDotThu(models.TextChoices):
    OPEN = "open", "Mở"
    CLOSED = "closed", "Đóng"
