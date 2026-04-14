from django import forms

from .models import KhoanThu
from .models import DotThuPhi

from datetime import datetime


class ReservationForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    check_in = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    num_guests = forms.IntegerField(min_value=1, initial=1)


class KhoanThuForm(forms.ModelForm):
    phi_bat_buoc = forms.TypedChoiceField(
        choices=[(True, 'Bắt buộc'), (False, 'Tự nguyện')],
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=True,
        label='Loại phí',
        required=False
    )

    class Meta:
        model = KhoanThu
        fields = ['ten_khoanthu', 'don_gia', 'don_vi_tinh', 'phi_bat_buoc']
        labels = {
            'ten_khoanthu': 'Tên khoản thu',
            'don_gia': 'Đơn giá (VND)',
            'don_vi_tinh': 'Đơn vị tính',
        }
        widgets = {
            'ten_khoanthu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên khoản thu'}),
            'don_gia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập đơn giá (VND)'}),
            'don_vi_tinh': forms.Select(attrs={'class': 'form-control'}),
        }


class DotThuPhiForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chỉ lấy các KhoanThu chưa bị xóa
        self.fields['id_khoanthu'].queryset = KhoanThu.objects.filter(
            is_deleted=False)

        # Đặt placeholder động cho tên đợt thu
        now = datetime.now()
        self.fields['ten_dotthu'].widget.attrs[
            'placeholder'] = f"VD: Thu phí tháng {now.month}/{now.year}"

    class Meta:
        model = DotThuPhi
        fields = ['ten_dotthu', 'ngay_batdau', 'ngay_ketthuc',
                  'loai_dot_thu', 'trang_thai', 'id_khoanthu']
        labels = {
            'ten_dotthu': 'Tên đợt thu',
            'ngay_batdau': 'Ngày bắt đầu',
            'ngay_ketthuc': 'Ngày kết thúc',
            'loai_dot_thu': 'Loại đợt thu',
            'trang_thai': 'Trạng thái',
            'id_khoanthu': 'Khoản thu áp dụng',
        }
        widgets = {
            'loai_dot_thu': forms.Select(attrs={'class': 'form-control'}),
            'ten_dotthu': forms.TextInput(attrs={'class': 'form-control'}),
            'id_khoanthu': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'ngay_batdau': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ngay_ketthuc': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'trang_thai': forms.Select(attrs={'class': 'form-control'}),
        }
