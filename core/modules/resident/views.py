from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from openpyxl import Workbook
from django.utils import timezone
from .models import BienDongNhanKhau, HoKhau, NhanKhau, CanHo
from core.forms import HoKhauForm
from core.decorators import role_required
from django.db.models import Q


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
    if request.method == 'POST':
        form = HoKhauForm(request.POST)
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
        form = HoKhauForm()
    return render(request, 'resident/hokhau_add.html', {'form': form})


@login_required(login_url="login")
@role_required([1])
def hokhau_edit(request, pk):
    hokhau = get_object_or_404(HoKhau, pk=pk)
    if request.method == 'POST':
        form = HoKhauForm(request.POST, instance=hokhau)
        if form.is_valid():
            hokhau = form.save(commit=False)
            hokhau.updated_by = request.user.username if request.user.is_authenticated else 'Unknown'
            hokhau.save()
            messages.success(request, 'Cập nhật hộ khẩu thành công!')
            return redirect('hokhau_list')
    else:
        form = HoKhauForm(instance=hokhau)
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
def edit_nhan_khau(request, id_nhankhau):
    nk = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)
    if request.method == "POST":
        nk.ho_ten = request.POST.get("ho_ten")
        nk.ngay_sinh = request.POST.get("ngay_sinh") or None
        nk.cccd = request.POST.get("cccd") or None
        nk.quan_he_chu_ho = request.POST.get("quan_he_chu_ho") or None
        ho_khau_id = request.POST.get("ho_khau_id")

        if ho_khau_id:
            nk.id_hokhau_id = ho_khau_id

        nk.save()
        return redirect("nhan_khau_profile", id_nhankhau=nk.id_nhankhau)

    return render(request, "core/demomanage_edit.html", {"nhan_khau": nk})


@login_required(login_url="login")
def nhan_khau_profile(request, id_nhankhau):
    nhan_khau = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)
    return render(request, "core/nhan_khau_profile.html", {"nhan_khau": nhan_khau})


@login_required(login_url="login")
def nhan_khau_delete(request, id_nhankhau):
    exists = NhanKhau.objects.filter(id_nhankhau=id_nhankhau).exists()
    if exists:
        nhan_khau = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)
        nhan_khau.is_deleted = True
        nhan_khau.save()

    return render(request, "core/demomanage_delete.html")


@login_required(login_url="login")
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
def add_demo(request):
    if request.method == "POST":
        ho_ten = request.POST.get("ho_ten")
        ngay_sinh = request.POST.get("ngay_sinh")
        cccd = request.POST.get("cccd")
        quan_he_chu_ho = request.POST.get("quan_he_chu_ho")
        ho_khau_id = request.POST.get("ho_khau_id")
        loai_bien_dong_query = request.POST.get("loai_dang_ky_cu_tru")
        try:
            if HoKhau.objects.filter(id_hokhau=ho_khau_id).exists():
                nhan_khau = NhanKhau.objects.create(
                    ho_ten=ho_ten,
                    ngay_sinh=ngay_sinh or None,
                    cccd=cccd or None,
                    quan_he_chu_ho=quan_he_chu_ho or None,
                    id_hokhau_id=int(ho_khau_id),
                )
                BienDongNhanKhau.objects.create(
                    loai_biendong=loai_bien_dong_query,
                    ngay_batdau=timezone.now().date(),
                    id_nhankhau=nhan_khau,
                    ly_do="Dang ky nhan khau moi",
                )

        except HoKhau.DoesNotExist:
            pass

        return redirect("demomanage/adddemo")

    return render(request, "core/demomanage_add.html")


@login_required(login_url="login")
def demomanage(request):
    nhan_khau_list = NhanKhau.objects.filter(is_deleted=False)
    query = request.GET.get("search_id", "")
    if query:
        try:
            for a in nhan_khau_list:
                if a.id_nhankhau == int(query):
                    nhan_khau_list = [a]
        except ValueError:
            nhan_khau_list = NhanKhau.objects.all()

    data = []
    for nk in nhan_khau_list:
        bien_dong = (
            BienDongNhanKhau.objects.filter(
                id_nhankhau=nk).order_by("-ngay_batdau").first()
        )

        trang_thai = bien_dong.loai_biendong if bien_dong else "Chưa xác định"

        data.append({"nhan_khau": nk, "trang_thai": trang_thai})
    context = {
        "data": data,
        "query": query,
    }
    return render(request, "core/demomanage.html", context)


@login_required(login_url="login")
def biendong_list(request):
    biendongs = BienDongNhanKhau.objects.select_related(
        "id_nhankhau").order_by("-ngay_batdau")

    return render(
        request,
        "core/biendong_list.html",
        {"biendongs": biendongs},
    )


@login_required(login_url="login")
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


@login_required(login_url="login")
def demomanage_delete(request, id_hokhau):
    exists = HoKhau.objects.filter(id_hokhau=id_hokhau).exists()
    if exists:
        hr = get_object_or_404(HoKhau, id_hokhau=id_hokhau)
        hr.is_deleted = True
        hr.save()
    return render(request, "core/hrmanage_delete.html")
