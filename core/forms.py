
from core.modules.noti.models import ThongBao
from django import forms
from django.core.exceptions import ValidationError

from core.modules.resident.models import GuiXe
from .models import KhoanThu, DotThuPhi, Building, CanHo, HoKhau, TaiKhoan, BienDongNhanKhau, NhanKhau
from datetime import datetime


class TaiKhoanForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password1 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Mật khẩu")
    password2 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Xác nhận mật khẩu")
    vaitro = forms.ChoiceField(
        choices=[(1, 'Ban Quản lý'), (2, 'Cư dân'), (3, 'Kế toán')],
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'vaitro-taikhoan'}),
        required=True,
        label='Vai trò'
    )
    id_canho = forms.ChoiceField(
        required=False,
        label='Căn hộ (chỉ áp dụng cho Chủ hộ)',
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'canho-taikhoan'}),
        choices=[],
    )

    resident_status = forms.ChoiceField(
        required=False,
        label='Tình trạng cư trú',
        choices=[],
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'resident-status'}),
    )

    def __init__(self, *args, available_canho=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resident_status'].choices = [
            ('', '-- Chọn tình trạng --')] + list(getattr(HoKhau, 'RESIDENT_STT_CHOICES', []))
        if available_canho:
            self.fields['id_canho'].choices = [
                ("", "-- Chọn căn hộ --")
            ] + [
                (c.id_canho, c.so_can_ho)
                for c in available_canho
            ]


class TaiKhoanEditForm(forms.ModelForm):
    id_canho = forms.ChoiceField(
        required=False,
        label='Căn hộ',
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'canho-taikhoan'
        })
    )
    resident_status = forms.ChoiceField(
        required=False,
        label='Tình trạng cư trú',
        choices=[],
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'resident-status'}),
    )

    class Meta:
        model = TaiKhoan
        fields = ['username', 'vaitro']
        labels = {
            'username': 'Tên tài khoản',
            'vaitro': 'Vai trò',
        }

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên tài khoản'
            }),

            'vaitro': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'id': 'vaitro-taikhoan'
            }),
        }

    def __init__(self, *args, available_canho=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resident_status'].choices = [
            ('', '-- Chọn tình trạng --')] + list(getattr(HoKhau, 'RESIDENT_STT_CHOICES', []))
        # Dynamic dropdown căn hộ
        if available_canho:
            self.fields['id_canho'].choices = [
                ("", "-- Chọn căn hộ --")
            ] + [
                (c.id_canho, c.so_can_ho)
                for c in available_canho
            ]

        hokhau = HoKhau.objects.filter(
            id_chuho=self.instance,
            is_deleted=False,
            is_active=True
        ).first()

        if hokhau and hokhau.id_canho:
            self.fields['id_canho'].initial = hokhau.id_canho.id_canho
        if hokhau and hokhau.resident_status:
            self.fields['resident_status'].initial = hokhau.resident_status


class CanHoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['building'].queryset = Building.objects.filter(
            is_active=True, is_deleted=False).order_by("name")

    class Meta:
        model = CanHo
        fields = [
            'so_can_ho', 'dien_tich', 'floor', 'building', 'apartment_type'
        ]
        widgets = {
            'so_can_ho': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số căn hộ'}),
            'dien_tich': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập diện tích (m²)'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tầng'}),
            'building': forms.Select(attrs={'class': 'form-control'}),
            'apartment_type': forms.Select(choices=CanHo.APARTMENT_TYPE_CHOICES),
        }


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


class HoKhauForm(forms.ModelForm):
    def __init__(self, *args, available_canho=None, available_chuho=None, disabled_chuho=False, **kwargs):
        super().__init__(*args, **kwargs)
        if available_canho is not None:
            self.fields['id_canho'].queryset = available_canho
        if available_chuho is not None:
            self.fields['id_chuho'].queryset = available_chuho
        if disabled_chuho:
            self.fields['id_chuho'].widget.attrs['disabled'] = 'true'
        if self.instance and self.instance.pk:
            if self.instance.id_canho:
                self.fields['id_canho'].initial = self.instance.id_canho.pk
            if self.instance.id_chuho:
                self.fields['id_chuho'].initial = self.instance.id_chuho.pk

    class Meta:
        model = HoKhau
        fields = ['id_canho', 'id_chuho', 'resident_status']
        labels = {
            'id_canho': 'Căn hộ',
            'id_chuho': 'Chủ hộ',
            'resident_status': 'Tình trạng cư trú',
        }
        widgets = {
            'id_canho': forms.Select(attrs={'class': 'form-control'}),
            'id_chuho': forms.Select(attrs={'class': 'form-control', }),
            'resident_status': forms.Select(attrs={'class': 'form-control'}),
        }


class NhanKhauForm(forms.ModelForm):
    def __init__(self, *args, hokhau_avai=None, disabled_hokhau=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quan_he_chu_ho'].required = True
        if hokhau_avai is not None:
            self.fields['id_hokhau'].queryset = hokhau_avai
        if self.instance and self.instance.pk and self.instance.id_hokhau:
            self.fields['id_hokhau'].initial = self.instance.id_hokhau.pk
        if disabled_hokhau:
            self.fields['id_hokhau'].widget.attrs['disabled'] = 'true'

    class Meta:
        model = NhanKhau
        fields = ['id_hokhau', 'ho_ten', 'gioi_tinh', 'ngay_sinh', 'cccd',
                  'so_dien_thoai', 'email',
                  'quan_he_chu_ho']
        labels = {
            'ho_ten': 'Họ tên',
            'gioi_tinh': 'Giới tính',
            'ngay_sinh': 'Ngày sinh',
            'cccd': 'CCCD/CMND',
            'so_dien_thoai': 'Số điện thoại',
            'email': 'Email',
            'quan_he_chu_ho': 'Quan hệ với chủ hộ',
            'id_hokhau': 'Hộ khẩu',
        }
        widgets = {
            'id_hokhau': forms.Select(attrs={'class': 'form-control'}),
            'ho_ten': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ tên'}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-control'}),
            'ngay_sinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cccd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số CCCD/CMND'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email'}),
            'quan_he_chu_ho': forms.Select(attrs={'class': 'form-control'}),
        }


class BienDongForm(forms.ModelForm):
    class Meta:
        model = BienDongNhanKhau
        fields = ['loai_biendong', 'ngay_batdau', 'ngay_ketthuc', 'ly_do']
        widgets = {
            'ngay_batdau': forms.DateInput(attrs={'type': 'date'}),
            'ngay_ketthuc': forms.DateInput(attrs={'type': 'date'}),
            'ly_do': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Nhập lý do đăng ký...'}),
        }
        labels = {
            'loai_biendong': 'Loại trạng thái cư trú muốn đăng ký',
            'ngay_batdau': 'Ngày bắt đầu',
            'ngay_ketthuc': 'Ngày kết thúc',
            'ly_do': 'Lý do biến động',
        }

    def __init__(self, *args, **kwargs):
        self.nhan_khau = kwargs.pop('nhan_khau', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        ngay_batdau = cleaned_data.get('ngay_batdau')
        ngay_ketthuc = cleaned_data.get('ngay_ketthuc')
        if ngay_batdau and ngay_ketthuc and ngay_batdau > ngay_ketthuc:
            raise ValidationError(
                'Ngày bắt đầu không được lớn hơn ngày kết thúc.')
        # Kiểm tra ngày bắt đầu không nhỏ hơn ngày kết thúc của bản ghi chưa xóa liền trước
        if self.nhan_khau:
            prev_bd = self.nhan_khau.nhan_khau.filter(
                is_deleted=False).order_by('-ngay_batdau').first()
            if prev_bd:
                if prev_bd.ngay_ketthuc:
                    if ngay_batdau < prev_bd.ngay_ketthuc:
                        raise ValidationError({
                            'ngay_batdau': 'Ngày bắt đầu không được nhỏ hơn ngày kết thúc của biến động trước.'
                        })
                else:
                    if ngay_batdau < prev_bd.ngay_batdau:
                        raise ValidationError({
                            'ngay_batdau': 'Ngày bắt đầu không được nhỏ hơn ngày bắt đầu của biến động trước.'
                        })
        return cleaned_data


class GuiXeForm(forms.ModelForm):
    hokhau = forms.ModelChoiceField(
        queryset=HoKhau.objects.none(),
        label='Hộ khẩu',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, hokhau_qs=None, disabled_hokhau=False, initial_hokhau=None, **kwargs):
        super().__init__(*args, **kwargs)
        if hokhau_qs is not None:
            self.fields['hokhau'].queryset = hokhau_qs
        if disabled_hokhau:
            self.fields['hokhau'].widget.attrs['disabled'] = 'true'
        if initial_hokhau is not None:
            self.fields['hokhau'].initial = initial_hokhau
        # Nếu instance đã có hokhau thì set initial
        if self.instance and getattr(self.instance, 'hokhau', None):
            self.fields['hokhau'].initial = self.instance.hokhau.pk

    class Meta:
        model = GuiXe
        fields = ['hokhau', 'loai_xe', 'bien_so', 'mo_ta']
        widgets = {
            'loai_xe': forms.Select(attrs={'class': 'form-control'}),
            'bien_so': forms.TextInput(attrs={'class': 'form-control'}),
            'mo_ta': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ThongBaoForm(forms.ModelForm):
    class Meta:
        model = ThongBao
        fields = ['title', 'content', 'doi_tuong']
        labels = {
            'title': 'Tiêu đề',
            'content': 'Nội dung',
            'doi_tuong': 'Đối tượng nhận',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Nhập nội dung'}),
            'doi_tuong': forms.Select(attrs={'class': 'form-control'}),
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput, label="Mật khẩu hiện tại", required=True)
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, label="Mật khẩu mới", required=True)
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, label="Xác nhận mật khẩu mới", required=True)



"""
swagger
ticket
"""
