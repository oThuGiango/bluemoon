from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from openpyxl import Workbook
from django.utils import timezone

from .models import BienDongNhanKhau, HoKhau, NhanKhau


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


@login_required(login_url="login")
def hrmanage(request):
    print(2)
    ds_ho_khau = HoKhau.objects.all()
    query = request.GET.get("search_id", "")
    if query:
        try:
            for a in ds_ho_khau:
                if a.id_hokhau == int(query):
                    ds_ho_khau = [a]
        except ValueError:
            ds_ho_khau = HoKhau.objects.all()

    context = {
        "ho_khau_list": ds_ho_khau,
        "query": query,
    }

    return render(request, "core/hrmanage.html", context)


@login_required(login_url="login")
def hrmanage_delete(request, id_hokhau):
    exists = HoKhau.objects.filter(id_hokhau=id_hokhau).exists()
    if exists:
        hr = get_object_or_404(HoKhau, id_hokhau=id_hokhau)
        hr.is_deleted = True
    return render(request, "core/hrmanage_delete.html")


@login_required(login_url="login")
def add_hokhau(request):
    if request.method == "POST":
        so_can_ho = request.POST.get("so_can_ho")
        dien_tich = request.POST.get("dien_tich")

        if so_can_ho:
            try:
                dien_tich_value = float(dien_tich) if dien_tich else None
                HoKhau.objects.create(
                    so_can_ho=so_can_ho, dien_tich=dien_tich_value)
                messages.success(
                    request, f"Hộ khẩu căn {so_can_ho} đã được thêm thành công!")
            except ValueError:
                messages.error(request, "Giá trị diện tích không hợp lệ!")
        else:
            messages.error(request, "Vui lòng nhập số căn hộ!")

        return redirect("add_hokhau")

    return render(request, "core/add_hokhau.html")


@login_required(login_url="login")
def hokhau_detail(request, id_hokhau):
    print(3)
    hokhau = HoKhau.objects.get(id_hokhau=id_hokhau)
    print(hokhau.id_hokhau)
    thanh_vien = NhanKhau.objects.filter(
        id_hokhau_id=id_hokhau, is_deleted=False)

    return render(request, "core/hokhau_detail.html", {"hokhau": hokhau, "thanh_vien": thanh_vien})


@login_required(login_url="login")
def edit_hokhau(request, id_hokhau):
    hokhau = get_object_or_404(HoKhau, id_hokhau=id_hokhau)

    if request.method == "POST":
        so_can_ho = request.POST.get("so_can_ho")
        dien_tich = request.POST.get("dien_tich")

        if not so_can_ho:
            messages.error(request, "Số căn hộ không được để trống!")
        else:
            try:
                hokhau.so_can_ho = so_can_ho
                hokhau.dien_tich = float(dien_tich) if dien_tich else None
                hokhau.save()
                messages.success(
                    request, "Cập nhật thông tin hộ khẩu thành công!")
                return redirect("hrmanage")
            except ValueError:
                messages.error(request, "Diện tích phải là số hợp lệ!")

    return render(request, "core/hokhau_edit.html", {"hokhau": hokhau})


@login_required(login_url="login")
def HoKhaus_list(request):
    ho_khaus = HoKhau.objects.all()
    return render(request, "core/HoKhaus_list.html", {"HoKhaus": ho_khaus})
