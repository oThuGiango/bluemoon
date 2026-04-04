from django import forms

from .models import KhoanThu
from .models import DotThuPhi

class ReservationForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    check_in = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    num_guests = forms.IntegerField(min_value=1, initial=1)

class KhoanThuForm(forms.ModelForm):
    class Meta:
        model = KhoanThu
        fields = ['id_khoanthu','ten_khoanthu', 'don_gia', 'don_vi_tinh'] 
        widgets = {
            'id_khoanthu': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mã khoản thu(ID)'}),
            'ten_khoanthu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên khoản thu'}),
            'don_gia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập đơn giá (VND)'}),
            'don_vi_tinh': forms.Select(attrs={'class': 'form-control'}),
        }
class DotThuPhiForm(forms.ModelForm):
    class Meta:
        model  = DotThuPhi
        fields = ['id_dotthu', 'ten_dotthu', 'ngay_batdau', 'ngay_ketthuc' , 'trang_thai', 'id_khoanthu']
        widgets = {
            'id_dotthu': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VD: 123456'}),
            'ten_dotthu': forms.TextInput(attrs={'class': 'form-control','placeholder': 'VD: Thu phí tháng 9/2023'}),
            'id_khoanthu': forms.Select(attrs={'class': 'form-control'}),
            'ngay_batdau': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ngay_ketthuc': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'trang_thai': forms.Select(attrs={'class': 'form-control'}),
        }