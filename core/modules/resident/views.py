from django.db.models import Q, OuterRef, Subquery, DateField, Case, When, Value, CharField
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from openpyxl import Workbook
from django.utils import timezone
from .models import BienDongNhanKhau, HoKhau, NhanKhau, CanHo
from core.modules.account.models import TaiKhoan
from core.forms import HoKhauForm, NhanKhauForm
from core.decorators import role_required
from core.modules.base.models import LoaiBienDong


def get_user_hokhau_active(user):
    """Trả về queryset hộ khẩu active mà user là chủ hộ (nếu là cư dân), ngược lại trả về None."""
    if hasattr(user, 'vaitro') and getattr(user.vaitro, 'id_vaitro', None) == 2:
        return HoKhau.objects.filter(is_active=True, is_deleted=False, id_chuho=user)
    return None


@login_required(login_url="login")
@role_required([1, 2])
def nhankhau_list(request):
    search = request.GET.get('search', '').strip()
    loai_biendong = request.GET.get('loai_biendong', '').strip()
    user_hokhau = get_user_hokhau_active(request.user)
    qs = NhanKhau.objects.filter(
        is_deleted=False, id_hokhau__is_active=True, id_hokhau__is_deleted=False)
    if user_hokhau is not None:
        qs = qs.filter(id_hokhau__in=user_hokhau)
    if search:
        qs = qs.filter(
            Q(ho_ten__icontains=search) |
            Q(cccd__icontains=search) |
            Q(so_dien_thoai__icontains=search) |
            Q(email__icontains=search)
        )
    latest_bd_subquery = BienDongNhanKhau.objects.filter(
        id_nhankhau=OuterRef('pk')
    ).order_by('-ngay_batdau')
    qs = qs.annotate(
        latest_bd_ngay=Subquery(latest_bd_subquery.values(
            'ngay_batdau')[:1], output_field=DateField()),
        latest_bd_loai=Subquery(latest_bd_subquery.values('loai_biendong')[:1])
    )
    if loai_biendong:
        qs = qs.filter(latest_bd_loai=loai_biendong)
    qs = qs.order_by('-latest_bd_ngay')

    choices_dict = dict(LoaiBienDong.choices)

    qs = qs.annotate(
        latest_bd_loai_display=Case(
            *[
                When(latest_bd_loai=k, then=Value(v))
                for k, v in choices_dict.items()
            ],
            default=Value('-'),
            output_field=CharField()
        )
    )

    return render(request, 'resident/nhankhau/list.html', {
        'nhankhau_list': qs,
        'search': search,
        'loai_biendong': loai_biendong
    })


@login_required(login_url="login")
@role_required([1, 2])
def nhankhau_detail(request, pk):
    nk = get_object_or_404(NhanKhau, pk=pk, is_deleted=False)
    user_hokhau = get_user_hokhau_active(request.user)
    # Nếu là cư dân chỉ cho xem nhân khẩu thuộc hộ khẩu của mình
    if user_hokhau is not None and nk.id_hokhau not in user_hokhau:
        messages.error(request, 'Bạn không có quyền xem nhân khẩu này!')
        return redirect('nhankhau_list')
    return render(request, 'resident/nhankhau/detail.html', {'nk': nk})


@login_required(login_url="login")
@role_required([1, 2])
def nhankhau_add(request):
    user_hokhau = get_user_hokhau_active(request.user)
    hokhau_avai = user_hokhau if user_hokhau is not None else HoKhau.objects.filter(
        is_active=True, is_deleted=False)
    if request.method == 'POST':
        form = NhanKhauForm(request.POST, hokhau_avai=hokhau_avai)
        if form.is_valid():
            nk = form.save(commit=False)
            nk.updated_by = request.user.username
            nk.save()
            loai_bd = (
                nk.id_hokhau.resident_status if nk.id_hokhau and nk.id_hokhau.resident_status else 'tam_vang')
            BienDongNhanKhau.objects.create(
                loai_biendong=loai_bd,
                ngay_batdau=timezone.now().date(),
                ly_do="Đăng ký mới",
                id_nhankhau=nk,
                updated_by=request.user.username
            )
            messages.success(request, 'Đăng ký nhân khẩu thành công!')
            return redirect('nhankhau_list')
        else:
            # Lấy tất cả lỗi của form (bao gồm cả lỗi trường và lỗi chung)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label if field in form.fields else field}: {error}")
            # Nếu có lỗi chung (non_field_errors)
            for error in form.non_field_errors():
                messages.error(request, error)
            return redirect('nhankhau_list')
    else:
        form = NhanKhauForm(hokhau_avai=hokhau_avai)
    return render(request, 'resident/nhankhau/form.html', {'form': form, 'action': 'add'})


@login_required(login_url="login")
@role_required([1, 2])
def nhankhau_edit(request, pk):
    nk = get_object_or_404(NhanKhau, pk=pk, is_deleted=False)
    user_hokhau = get_user_hokhau_active(request.user)
    hokhau_avai = user_hokhau if user_hokhau is not None else HoKhau.objects.filter(
        is_active=True, is_deleted=False)
    if user_hokhau is not None and nk.id_hokhau not in user_hokhau:
        messages.error(request, 'Bạn không có quyền sửa nhân khẩu này!')
        return redirect('nhankhau_list')
    if request.method == 'POST':
        # Nếu trường id_hokhau bị disabled thì sẽ không có trong POST, nên gán lại từ instance
        post = request.POST.copy()
        post['id_hokhau'] = str(nk.id_hokhau.pk) if nk.id_hokhau else ''
        form = NhanKhauForm(post, instance=nk,
                            hokhau_avai=hokhau_avai, disabled_hokhau=True)
        if form.is_valid():
            nk = form.save(commit=False)
            nk.updated_by = request.user.username
            nk.save()
            return redirect('nhankhau_detail', pk=nk.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label if field in form.fields else field}: {error}")
            for error in form.non_field_errors():
                messages.error(request, error)
            return redirect('nhankhau_list')
    else:
        form = NhanKhauForm(
            instance=nk, hokhau_avai=hokhau_avai, disabled_hokhau=True)
    return render(request, 'resident/nhankhau/edit_form.html', {'form': form, 'action': 'edit', 'nk': nk})


@login_required(login_url="login")
@role_required([1, 2])
def nhankhau_delete(request, pk):
    nk = get_object_or_404(NhanKhau, pk=pk, is_deleted=False)
    user_hokhau = get_user_hokhau_active(request.user)
    # Nếu là cư dân chỉ cho xóa nhân khẩu thuộc hộ khẩu của mình
    if user_hokhau is not None and nk.id_hokhau not in user_hokhau:
        messages.error(request, 'Bạn không có quyền xóa nhân khẩu này!')
        return redirect('nhankhau_list')
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
    available_canho = CanHo.objects.filter(is_deleted=False).exclude(
        id_canho__in=canho_with_active_hokhau)
    # Lấy danh sách chủ hộ chưa có hộ khẩu active
    chuho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_chuho__isnull=False).values_list('id_chuho', flat=True)
    available_chuho = TaiKhoan.objects.filter(vaitro__id_vaitro=2, is_deleted=False, is_active=True).exclude(
        id_taikhoan__in=chuho_with_active_hokhau)

    if request.method == 'POST':
        form = HoKhauForm(
            request.POST, available_canho=available_canho, available_chuho=available_chuho)
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
            # Lấy tất cả lỗi của form (bao gồm cả lỗi trường và lỗi chung)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label if field in form.fields else field}: {error}")
            # Nếu có lỗi chung (non_field_errors)
            for error in form.non_field_errors():
                messages.error(request, error)
            return redirect('hokhau_list')
    else:
        form = HoKhauForm(available_canho=available_canho,
                          available_chuho=available_chuho)
    return render(request, 'resident/hokhau_add.html', {'form': form})


@login_required(login_url="login")
@role_required([1])
def hokhau_edit(request, pk):
    hokhau = get_object_or_404(HoKhau, pk=pk)
    # Lấy danh sách căn hộ chưa có hộ khẩu active, cộng thêm căn hộ hiện tại
    canho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_canho__isnull=False).values_list('id_canho', flat=True)
    available_canho = CanHo.objects.filter(is_deleted=False).exclude(
        id_canho__in=canho_with_active_hokhau)
    if hokhau.id_canho:
        available_canho = available_canho | CanHo.objects.filter(
            id_canho=hokhau.id_canho.id_canho)
    # Lấy danh sách chủ hộ chưa có hộ khẩu active, cộng thêm chủ hộ hiện tại
    chuho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_chuho__isnull=False).values_list('id_chuho', flat=True)
    available_chuho = TaiKhoan.objects.filter(vaitro__id_vaitro=2, is_deleted=False, is_active=True).exclude(
        id_taikhoan__in=chuho_with_active_hokhau)
    if hokhau.id_chuho:
        available_chuho = available_chuho | TaiKhoan.objects.filter(
            id_taikhoan=hokhau.id_chuho.id_taikhoan)

    if request.method == 'POST':
        post = request.POST.copy()
        post['id_chuho'] = str(hokhau.id_chuho.pk)
        form = HoKhauForm(post, instance=hokhau, available_canho=available_canho,
                          available_chuho=available_chuho, disabled_chuho=True)
        if form.is_valid():
            hokhau = form.save(commit=False)
            hokhau.updated_by = request.user.username if request.user.is_authenticated else 'Unknown'
            hokhau.save()
            messages.success(request, 'Cập nhật hộ khẩu thành công!')
            return redirect('hokhau_list')
        else:
            # Lấy tất cả lỗi của form (bao gồm cả lỗi trường và lỗi chung)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label if field in form.fields else field}: {error}")
            # Nếu có lỗi chung (non_field_errors)
            for error in form.non_field_errors():
                messages.error(request, error)
            return redirect('hokhau_list')
    else:
        form = HoKhauForm(instance=hokhau, available_canho=available_canho,
                          available_chuho=available_chuho, disabled_chuho=True)
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
