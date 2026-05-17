from django.db.models import Q
from core.decorators import role_required
from core.forms import HoKhauForm
from core.modules.account.models import TaiKhoan
from .models import BienDongNhanKhau, HoKhau, NhanKhau, CanHo
from django.utils import timezone
from openpyxl import Workbook
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django import forms


class NhanKhauForm(forms.ModelForm):
    class Meta:
        model = NhanKhau
        fields = ['ho_ten', 'gioi_tinh', 'ngay_sinh', 'cccd',
                  'quan_he_chu_ho', 'id_hokhau', 'is_active']


@login_required(login_url="login")
@role_required([1])
def nhankhau_list(request):
    search = request.GET.get('search', '').strip()
    qs = NhanKhau.objects.filter(is_deleted=False)
    if search:
        qs = qs.filter(ho_ten__icontains=search)
    return render(request, 'resident/nhankhau/list.html', {'nhankhau_list': qs, 'search': search})


@login_required(login_url="login")
@role_required([1])
def nhankhau_detail(request, pk):
    nk = get_object_or_404(NhanKhau, pk=pk, is_deleted=False)
    return render(request, 'resident/nhankhau/detail.html', {'nk': nk})


@login_required(login_url="login")
@role_required([1])
def nhankhau_add(request):
    if request.method == 'POST':
        form = NhanKhauForm(request.POST)
        if form.is_valid():
            nk = form.save(commit=False)
            nk.updated_by = request.user.username
            nk.save()
            return redirect('nhankhau_list')
    else:
        form = NhanKhauForm()
    return render(request, 'resident/nhankhau/form.html', {'form': form, 'action': 'add'})


@login_required(login_url="login")
@role_required([1])
def nhankhau_edit(request, pk):
    nk = get_object_or_404(NhanKhau, pk=pk, is_deleted=False)
    if request.method == 'POST':
        form = NhanKhauForm(request.POST, instance=nk)
        if form.is_valid():
            nk = form.save(commit=False)
            nk.updated_by = request.user.username
            nk.save()
            return redirect('nhankhau_detail', pk=nk.pk)
    else:
        form = NhanKhauForm(instance=nk)
    return render(request, 'resident/nhankhau/form.html', {'form': form, 'action': 'edit', 'nk': nk})


@login_required(login_url="login")
@role_required([1])
def nhankhau_delete(request, pk):
    nk = get_object_or_404(NhanKhau, pk=pk, is_deleted=False)
    if request.method == 'POST':
        nk.is_deleted = True
        nk.save()
        return redirect('nhankhau_list')
    return render(request, 'resident/nhankhau/confirm_delete.html', {'nk': nk})


@login_required(login_url="login")
@role_required([1])
def hokhau_toggle_active(request, pk):
    hokhau = get_object_or_404(HoKhau, pk=pk)
    if request.method == 'POST':
        hokhau.is_active = not hokhau.is_active
        hokhau.save(update_fields=['is_active', 'updated_at'])
        messages.success(
            request, f'Trạng thái hộ khẩu đã được cập nhật thành {"hoạt động" if hokhau.is_active else "không hoạt động"}!')
    return redirect('hokhau_list')


@login_required(login_url="login")
@role_required([1])
def hokhau_list(request):
    hokhau_qs = HoKhau.objects.filter(is_deleted=False).select_related(
        'id_canho', 'id_chuho').order_by('-id_hokhau')

    search_hk = request.GET.get('search_hk', '').strip()
    resident_status = request.GET.get('resident_status', '')
    is_active = request.GET.get('is_active', '')

    if search_hk:
        hokhau_qs = hokhau_qs.filter(
            Q(id_canho__so_can_ho__icontains=search_hk) |
            Q(id_chuho__username__icontains=search_hk)
        )
    if resident_status:
        hokhau_qs = hokhau_qs.filter(resident_status=resident_status)
    if is_active in ['0', '1']:
        hokhau_qs = hokhau_qs.filter(is_active=(is_active == '1'))

    # Đếm số nhân khẩu cho từng hộ khẩu
    nhankhau_counts = {}
    from core.modules.resident.models import NhanKhau
    for hk in hokhau_qs:
        nhankhau_counts[hk.id_hokhau] = NhanKhau.objects.filter(
            id_hokhau=hk, is_deleted=False, is_active=True).count()

    total_count = hokhau_qs.count()
    return render(request, 'resident/hokhau.html', {
        'hokhau_list': hokhau_qs,
        'nhankhau_counts': nhankhau_counts,
        'search_hk': search_hk,
        'resident_status': resident_status,
        'is_active': is_active,
        'total_count': total_count,
    })


@login_required(login_url="login")
@role_required([1])
def hokhau_add(request):
    # Lấy danh sách căn hộ chưa có hộ khẩu active
    canho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_canho__isnull=False).values_list('id_canho', flat=True)
    available_canho = CanHo.objects.filter(is_deleted=False).exclude(id_canho__in=canho_with_active_hokhau)
    # Lấy danh sách chủ hộ chưa có hộ khẩu active
    chuho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_chuho__isnull=False).values_list('id_chuho', flat=True)
    available_chuho = TaiKhoan.objects.filter(vaitro__id_vaitro=2, is_deleted=False, is_active=True).exclude(id_taikhoan__in=chuho_with_active_hokhau)

    if request.method == 'POST':
        form = HoKhauForm(request.POST, available_canho=available_canho, available_chuho=available_chuho)
        if form.is_valid():
            id_canho = form.cleaned_data.get('id_canho')
            id_chuho = form.cleaned_data.get('id_chuho')
            # Nếu form là ModelForm thì lấy instance, nếu không thì lấy từ cleaned_data
            if hasattr(form, 'instance') and form.instance:
                id_canho = form.instance.id_canho or id_canho
                id_chuho = form.instance.id_chuho or id_chuho
            # Kiểm tra bản ghi đã tồn tại nhưng đang is_active=False
            existing = None
            if id_canho and id_chuho:
                existing = HoKhau.objects.filter(
                    id_canho=id_canho, id_chuho=id_chuho, is_deleted=False, is_active=False).first()
            if existing:
                existing.is_active = True
                existing.updated_by = request.user.username if request.user.is_authenticated else 'Unknown'
                existing.save(
                    update_fields=['is_active', 'updated_by', 'updated_at'])
                messages.success(request, 'Đã kích hoạt lại hộ khẩu cũ!')
                return redirect('hokhau_list')
            else:
                hokhau = form.save(commit=False)
                hokhau.updated_by = request.user.username if request.user.is_authenticated else 'Unknown'
                hokhau.save()
                messages.success(request, 'Thêm hộ khẩu thành công!')
                return redirect('hokhau_list')
    else:
        form = HoKhauForm(available_canho=available_canho, available_chuho=available_chuho)
    return render(request, 'resident/hokhau_add.html', {'form': form})


@login_required(login_url="login")
@role_required([1])
def hokhau_edit(request, pk):
    hokhau = get_object_or_404(HoKhau, pk=pk)
    # Lấy danh sách căn hộ chưa có hộ khẩu active, cộng thêm căn hộ hiện tại
    canho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_canho__isnull=False).values_list('id_canho', flat=True)
    available_canho = CanHo.objects.filter(is_deleted=False).exclude(id_canho__in=canho_with_active_hokhau)
    if hokhau.id_canho:
        available_canho = available_canho | CanHo.objects.filter(id_canho=hokhau.id_canho.id_canho)
    # Lấy danh sách chủ hộ chưa có hộ khẩu active, cộng thêm chủ hộ hiện tại
    chuho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_chuho__isnull=False).values_list('id_chuho', flat=True)
    available_chuho = TaiKhoan.objects.filter(vaitro__id_vaitro=2, is_deleted=False, is_active=True).exclude(id_taikhoan__in=chuho_with_active_hokhau)
    if hokhau.id_chuho:
        available_chuho = available_chuho | TaiKhoan.objects.filter(id_taikhoan=hokhau.id_chuho.id_taikhoan)

    if request.method == 'POST':
        post = request.POST.copy()
        post['id_chuho'] = str(hokhau.id_chuho.pk)
        form = HoKhauForm(post, instance=hokhau, available_canho=available_canho, available_chuho=available_chuho,disabled_chuho=True)
        if form.is_valid():
            hokhau = form.save(commit=False)
            hokhau.updated_by = request.user.username if request.user.is_authenticated else 'Unknown'
            hokhau.save()
            messages.success(request, 'Cập nhật hộ khẩu thành công!')
            return redirect('hokhau_list')
    else:
        form = HoKhauForm(instance=hokhau, available_canho=available_canho, available_chuho=available_chuho,disabled_chuho=True)
    return render(request, 'resident/hokhau_edit.html', {'form': form, 'hokhau': hokhau})


@login_required(login_url="login")
@role_required([1])
def hokhau_delete(request, pk):
    hokhau = get_object_or_404(HoKhau, pk=pk)
    if request.method == 'POST':
        hokhau.is_deleted = True
        hokhau.updated_by = request.user.username if request.user.is_authenticated else 'Unknown'
        hokhau.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
        messages.success(request, 'Đã xóa hộ khẩu!')
        return redirect('hokhau_list')
    return render(request, 'resident/hokhau_delete.html', {'hokhau': hokhau})


@login_required(login_url="login")
@role_required([1, 2])
def hokhau_detail(request, pk):
    hokhau = get_object_or_404(HoKhau, pk=pk)
    nhankhau_list = NhanKhau.objects.filter(
        id_hokhau=hokhau, is_deleted=False, is_active=True)
    nhankhau_count = nhankhau_list.count()
    return render(request, 'resident/hokhau_detail.html', {
        'hokhau': hokhau,
        'nhankhau_list': nhankhau_list,
        'nhankhau_count': nhankhau_count
    })


@login_required(login_url="login")
@role_required([1, 2])
def nhan_khau_profile(request, id_nhankhau):
    nhan_khau = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)
    return render(request, "core/nhan_khau_profile.html", {"nhan_khau": nhan_khau})


@login_required(login_url="login")
@role_required([1, 2])
def export_biendong_excel(request):
    biendongs = BienDongNhanKhau.objects.select_related(
        "id_nhankhau").order_by("-ngay_batdau")

    wb = Workbook()
    ws = wb.active
    ws.title = "Biến động nhân khẩu"

    ws.append([
        "ID Biến động",
        "Họ tên",
        "Loại biến động",
        "Ngày bắt đầu",
        "Ngày kết thúc",
        "Lý do",
    ])

    for bd in biendongs:
        ws.append([
            bd.id_biendong,
            bd.id_nhankhau.ho_ten,
            bd.loai_biendong,
            bd.ngay_batdau.strftime("%d/%m/%Y") if bd.ngay_batdau else "",
            bd.ngay_ketthuc.strftime("%d/%m/%Y") if bd.ngay_ketthuc else "",
            bd.ly_do or "",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="biendong_nhankhau.xlsx"'

    wb.save(response)
    return response


@login_required(login_url="login")
@role_required([1, 2])
def export_nhankhau_excel(request):
    nhankhau = NhanKhau.objects.filter(is_deleted=False)

    wb = Workbook()
    ws = wb.active
    ws.title = "Danh sách nhân khẩu"

    ws.append([
        "ID Nhân khẩu",
        "Họ tên",
        "Ngày sinh",
        "CCCD",
        "Quan hệ chủ hộ",
        "ID hộ khẩu",
    ])

    for nk in nhankhau:
        ws.append([
            nk.id_nhankhau,
            nk.ho_ten,
            nk.ngay_sinh,
            nk.cccd,
            nk.quan_he_chu_ho,
            nk.id_nhankhau,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="danh_sach_nhan_khau.xlsx"'

    wb.save(response)
    return response


@login_required(login_url="login")
@role_required([1, 2])
def export_hokhau_excel(request):
    hokhau = HoKhau.objects.filter(is_deleted=False)

    wb = Workbook()
    ws = wb.active
    ws.title = "Biến động nhân khẩu"

    ws.append([
        "ID Hộ Khẩu",
        "Số căn hộ",
        "Diện tích",
    ])

    for hk in hokhau:
        ws.append([
            hk.id_hokhau,
            hk.so_can_ho,
            hk.dien_tich,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="danh_sach_ho_khau.xlsx"'

    wb.save(response)
    return response


@login_required(login_url="login")
@role_required([1, 2])
def biendong_list(request):
    biendongs = BienDongNhanKhau.objects.select_related(
        "id_nhankhau").order_by("-ngay_batdau")

    return render(
        request,
        "core/biendong_list.html",
        {"biendongs": biendongs},
    )


@login_required(login_url="login")
@role_required([1, 2])
def dang_ky_bdbk(request, id_nhankhau):
    nhan_khau = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)

    if request.method == "POST":
        ngay_batdau = request.POST.get("ngay_batdau")
        ngay_ketthuc = request.POST.get("ngay_ketthuc")
        loai_bien_dong = request.POST.get("loai_bien_dong")
        ly_do = request.POST.get("ly_do")

        with transaction.atomic():
            BienDongNhanKhau.objects.create(
                loai_biendong=loai_bien_dong,
                ngay_batdau=ngay_batdau or timezone.now().date(),
                ngay_ketthuc=ngay_ketthuc or None,
                ly_do=ly_do or None,
                id_nhankhau=nhan_khau,
            )

        return redirect("biendong_list")

    return render(
        request,
        "core/dangkybdnk.html",
        {"nhan_khau": nhan_khau},
    )
