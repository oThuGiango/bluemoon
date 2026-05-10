import json

from core.decorators import role_required
from .models import DotThuPhi, HoaDon, KhoanThu, HoaDonChiTiet
from core.modules.resident.models import HoKhau
from core.forms import DotThuPhiForm, KhoanThuForm
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl import Workbook
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count, Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime


def calculate_invoice(tat_ca_ho_khau, khoanthu_objs):
    """
    Return:
      tong_tien_ho: dict[id_hokhau] = {"tong": ..., "chi_tiet": [...], "so_can_ho": ...}
      tong_tien_dot: tổng toàn đợt
    """
    tong_tien_ho = {}
    tong_tien_dot = 0
    for hokhau in tat_ca_ho_khau:
        tong = 0
        chi_tiet = []
        canho = hokhau.id_canho
        dien_tich = float(canho.dien_tich or 0) if canho else 0
        so_can_ho = canho.so_can_ho if canho else ""
        for kt in khoanthu_objs:
            if kt.don_vi_tinh == "dientich":
                so_luong = dien_tich
                so_tien = float(kt.don_gia) * so_luong
            else:
                so_luong = 1
                so_tien = float(kt.don_gia)

            chi_tiet.append({
                "id_khoanthu": kt.id_khoanthu,
                "khoanthu": kt.ten_khoanthu,
                "so_tien": so_tien,
                "so_luong": so_luong
            })
            tong += so_tien
        tong_tien_ho[hokhau.id_hokhau] = {
            "tong": tong, "chi_tiet": chi_tiet, "so_can_ho": so_can_ho}
        tong_tien_dot += tong
    return tong_tien_ho, tong_tien_dot


@login_required(login_url="login")
@role_required([3])
def fee_management(request):
    query = request.GET.get("search_khoanthu")
    khoan_thu_list = KhoanThu.objects.filter(
        is_deleted=False).order_by('id_khoanthu')

    if query:
        khoan_thu_list = khoan_thu_list.filter(
            (Q(ten_khoanthu__icontains=query) | Q(
                id_khoanthu__icontains=query)) & Q(is_deleted=False)
        ).order_by('id_khoanthu')
    total_count = khoan_thu_list.count()
    form = KhoanThuForm()
    context = {
        "khoan_thu_list": khoan_thu_list,
        "total_count": total_count,
        "form": form,
        "query": query,
    }
    return render(request, "fee/FeeManagement.html", context)


@login_required(login_url="login")
@role_required([3])
def view_khoanthu_detail_modal(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        pass
    return render(request, "fee/ViewFeeDetailModal.html", {"khoan_thu": khoan_thu})


@login_required(login_url="login")
@role_required([3])
def add_khoanthu(request):
    if request.method == "POST":
        form = KhoanThuForm(request.POST)
        if form.is_valid():
            ten_khoanthu = form.cleaned_data.get("ten_khoanthu").strip()
            if KhoanThu.objects.filter(ten_khoanthu__iexact=ten_khoanthu).exists():
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"error": "Tên khoản thu này đã tồn tại!"}, status=400)
                messages.error(request, "Tên khoản thu này đã tồn tại!")
                return redirect("fee_management")

            khoan_thu = form.save(commit=False)
            # if not khoan_thu.phi_bat_buoc:
            #     khoan_thu.don_gia = 1
            if request.user.is_authenticated:
                khoan_thu.updated_by = str(request.user)
            khoan_thu.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})
            messages.success(request, "Thêm khoản thu thành công!")
            return redirect("fee_management")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"error": "Dữ liệu không hợp lệ!"}, status=400)
    else:
        form = KhoanThuForm()
    return render(request, "fee/AddFeeModal.html", {"form": form})


@login_required(login_url="login")
@role_required([3])
def edit_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)

    if request.method == "POST":
        form = KhoanThuForm(request.POST, instance=khoan_thu)
        if form.is_valid():
            khoan_thu = form.save(commit=False)
            # if not khoan_thu.phi_bat_buoc:
            #     khoan_thu.don_gia = 1
            khoan_thu.updated_at = timezone.now()
            if request.user.is_authenticated:
                khoan_thu.updated_by = str(request.user)
            khoan_thu.save(update_fields=[
                field for field in ["ten_khoanthu", "don_gia", "phi_bat_buoc", "updated_at", "updated_by"] if hasattr(khoan_thu, field)
            ])
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})
            messages.success(
                request, f"Khoản thu '{khoan_thu.ten_khoanthu}' đã được cập nhật thành công!")
            return redirect("fee_management")
        else:
            context = {"form": form, "khoan_thu": khoan_thu}
            return render(request, "fee/EditFeeModal.html", context, status=400)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = KhoanThuForm(instance=khoan_thu)
        context = {"form": form, "khoan_thu": khoan_thu}
        return render(request, "fee/EditFeeModal.html", context)
    else:
        form = KhoanThuForm(instance=khoan_thu)
        context = {
            "form": form,
            "khoan_thu": khoan_thu,
            "page_title": f"CHỈNH SỬA KHOẢN THU - {khoan_thu.ten_khoanthu}",
        }
        return render(request, "fee/EditFeeModal.html", context)


@login_required(login_url="login")
@role_required([3])
def delete_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)

    if request.method == "POST":
        khoan_thu.is_deleted = True
        khoan_thu.updated_at = timezone.now()
        if request.user.is_authenticated:
            khoan_thu.updated_by = str(request.user)
        khoan_thu.save(
            update_fields=["is_deleted", "updated_at", "updated_by"])
        messages.success(
            request, f"Khoản thu '{khoan_thu.ten_khoanthu}' đã được xóa thành công!")
        return redirect("fee_management")

    return render(request, "fee/DeleteFeeModal.html", {"khoan_thu": khoan_thu})


@login_required(login_url="login")
@role_required([3])
def fee_collection_period(request):
    query = request.GET.get("search_dotthu")
    dot_thu_phi_list = DotThuPhi.objects.prefetch_related(
        "id_khoanthu").filter(is_deleted=False)
    active_count = dot_thu_phi_list.filter(
        trang_thai="open", is_deleted=False).count()
    if query:
        dot_thu_phi_list = dot_thu_phi_list.filter(
            (Q(ten_dotthu__icontains=query) | Q(
                id_dotthu__icontains=query))
        )
    context = {
        "dot_thu_phi_list": dot_thu_phi_list,
        "active_count": active_count,
        "query": query,
    }
    return render(request, "period/FeeCollectionPeriod.html", context)


# Trang chi tiết đợt thu phí (page, không phải modal)
@login_required(login_url="login")
@role_required([3])
def fee_collection_period_detail(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    danh_sach_hoa_don = dot_thu.hoa_dons.select_related(
        "id_hokhau", "id_hokhau__id_canho").filter(is_deleted=False).order_by("id_hokhau__id_canho__so_can_ho")
    ids_da_co = danh_sach_hoa_don.values_list("id_hokhau_id", flat=True)
    tat_ca_ho_khau = HoKhau.objects.filter(
        is_active=True, is_deleted=False).exclude(id_hokhau__in=ids_da_co)
    khoanthu_objs = list(dot_thu.id_khoanthu.all())
    khoanthu_list = [
        {"id_khoanthu": kt.id_khoanthu, "ten_khoanthu": kt.ten_khoanthu,
            "don_gia": kt.don_gia, "don_vi_tinh": kt.don_vi_tinh}
        for kt in khoanthu_objs
    ]

    tong_tien_ho, tong_tien_dot = calculate_invoice(
        tat_ca_ho_khau, khoanthu_objs)

    context = {
        "dot_thu": dot_thu,
        "danh_sach_hoa_don": danh_sach_hoa_don,
        "tat_ca_ho_khau": tat_ca_ho_khau,
        "khoanthu_list": khoanthu_list,
        "tong_tien_ho": tong_tien_ho,
        "tong_tien_dot": tong_tien_dot,
    }
    return render(request, "period/FeeCollectionPeriodDetail.html", context)


@login_required(login_url="login")
@role_required([3])
def update_payment_status(request):
    invoice_ids = request.POST.getlist("invoice_ids[]")

    if not invoice_ids:
        return JsonResponse({"status": "error", "message": "Không có hóa đơn nào được chọn"}, status=400)

    try:
        # Lấy các hóa đơn cần cập nhật
        invoices = HoaDon.objects.filter(
            id_hoadon__in=invoice_ids, ngay_nop__isnull=True, is_deleted=False)
        for invoice in invoices:
            invoice.ngay_nop = timezone.now()
            invoice.da_dong = invoice.tong_tien
            if request.user.is_authenticated:
                invoice.updated_by = str(request.user)
            invoice.save(update_fields=["ngay_nop",
                         "da_dong", "updated_by"])
        return JsonResponse({"status": "success", "message": "Cập nhật trạng thái thành công"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required(login_url="login")
@role_required([3])
def create_invoices_for_period(request):
    id_dotthu = request.POST.get("id_dotthu")
    hokhau_data = json.loads(request.POST.get("hokhau_data"))

    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=id_dotthu)

    for ho in hokhau_data:
        id_hokhau = ho["id_hokhau"]
        tong_tien = ho["tong"]
        chi_tiet = ho.get("chi_tiet", [])
        hokhau = HoKhau.objects.get(pk=id_hokhau)
        hoadon, created = HoaDon.objects.get_or_create(
            id_dotthu=dot_thu,
            id_hokhau=hokhau,
            defaults={"tong_tien": tong_tien},
        )

        # Cập nhật updated_at, updated_by khi tạo hoặc khôi phục hóa đơn
        if request.user.is_authenticated:
            hoadon.updated_by = str(request.user)
        if not created and getattr(hoadon, "is_deleted", False):
            hoadon.is_deleted = False
            hoadon.save(update_fields=["is_deleted",
                        "updated_by"])
        else:
            hoadon.save(update_fields=["updated_by"])

        for ct in chi_tiet:
            khoanthu = KhoanThu.objects.get(pk=ct["id_khoanthu"])

            HoaDonChiTiet.objects.get_or_create(
                hoadon=hoadon,
                khoanthu=khoanthu,
                defaults={
                    "so_luong": ct["so_luong"],
                    "thanh_tien": ct["so_tien"]
                }
            )

    danh_sach_hoa_don = dot_thu.hoa_dons.select_related(
        "id_hokhau", "id_hokhau__id_canho").all().order_by("id_hokhau__id_canho__so_can_ho")
    tat_ca_ho_khau = HoKhau.objects.exclude(
        id_hokhau__in=danh_sach_hoa_don.values_list("id_hokhau_id", flat=True))

    context = {
        "dot_thu": dot_thu,
        "danh_sach_hoa_don": danh_sach_hoa_don,
        "tat_ca_ho_khau": tat_ca_ho_khau,
        # "khoanthu_list": khoanthu_list,
        # "tong_tien_ho": tong_tien_ho,
        # "tong_tien_dot": tong_tien_dot,
    }

    return render(
        request,
        "period/FeeCollectionPeriodDetail.html", context
    )


@login_required(login_url="login")
@role_required([3])
def add_dotthu(request):
    if request.method == "POST":
        form = DotThuPhiForm(request.POST)
        if form.is_valid():
            ngay_batdau = form.cleaned_data.get("ngay_batdau")
            trang_thai = form.cleaned_data.get("trang_thai")
            id_khoanthu = form.cleaned_data.get("id_khoanthu")

            # Kiểm tra trùng đợt thu phí (nếu cần, có thể cần sửa lại điều kiện cho phù hợp ManyToMany)
            # if DotThuPhi.objects.filter(ngay_batdau=ngay_batdau, trang_thai=trang_thai, id_khoanthu__in=id_khoanthu).exists():
            #     return JsonResponse({"error": "Đợt thu phí này đã tồn tại (trùng mã hoặc trùng ngày bắt đầu, trạng thái, khoản thu)!"}, status=400)

            instance = form.save(commit=False)
            if request.user.is_authenticated:
                instance.updated_by = str(request.user)
            instance.save()
            form.save_m2m()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})

            return redirect("fee_collection_period")
    else:
        form = DotThuPhiForm()
    return render(request, "period/AddPeriodModal.html", {"form": form})


@login_required(login_url="login")
@role_required([3])
def edit_dotthu(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    if request.method == "POST":
        form = DotThuPhiForm(request.POST, instance=dot_thu)
        if form.is_valid():
            ngay_batdau = form.cleaned_data.get("ngay_batdau")
            trang_thai = form.cleaned_data.get("trang_thai")
            id_khoanthu = form.cleaned_data.get("id_khoanthu")
            # # Nếu chỉ cần trùng 1 khoản thu là báo lỗi:
            # qs = DotThuPhi.objects.exclude(id_dotthu=pk).filter(
            #     ngay_batdau=ngay_batdau, trang_thai=trang_thai, id_khoanthu__in=id_khoanthu
            # )
            # if qs.exists():
            #     return JsonResponse({"error": "Đợt thu phí này đã tồn tại (trùng mã hoặc trùng ngày bắt đầu, trạng thái, khoản thu)!"}, status=400)

            dot_thu = form.save(commit=False)
            dot_thu.updated_at = timezone.now()
            if request.user.is_authenticated:
                dot_thu.updated_by = str(request.user)
            dot_thu.save(update_fields=[
                field for field in ["ten_dotthu", "ngay_batdau", "ngay_ketthuc", "trang_thai", "updated_by"] if hasattr(dot_thu, field)
            ])
            form.save_m2m()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})
            return redirect("fee_collection_period")
        else:
            return render(request, "period/EditPeriodModal.html", {"form": form, "dot_thu": dot_thu}, status=400)

    form = DotThuPhiForm(instance=dot_thu)
    return render(request, "period/EditPeriodModal.html", {"form": form, "dot_thu": dot_thu})


@login_required(login_url="login")
@role_required([3])
def delete_dotthu(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    if request.method == "POST":
        dot_thu.is_deleted = True
        dot_thu.updated_at = timezone.now()
        if request.user.is_authenticated:
            dot_thu.updated_by = str(request.user)
        dot_thu.save(update_fields=["is_deleted", "updated_at", "updated_by"])
        messages.success(
            request, f"Đợt thu phí '{dot_thu.ten_dotthu}' đã được xóa thành công!")
        return redirect("fee_collection_period")
    return render(request, "period/DeletePeriodModal.html", {"dot_thu": dot_thu})


@login_required(login_url="login")
def statistics_view(request):
    year_str = request.GET.get("year", str(datetime.now().year))
    try:
        year = int(year_str)
    except ValueError:
        year = datetime.now().year

    khoanthu_filter = {
        'dot_thuphi__hoa_dons__ngay_nop__year': year,
        'dot_thuphi__is_deleted': False,
        'dot_thuphi__hoa_dons__is_deleted': False,
    }
    hoadon_filter = {
        'ngay_nop__year': year,
        'is_deleted': False,
    }
    tong_da_thu_filter = {
        'ngay_nop__year': year,
        'is_deleted': False,
    }
    tong_can_thu_filter = {
        'id_dotthu__in': DotThuPhi.objects.filter(ngay_batdau__year=year, is_deleted=False),
        'is_deleted': False,
    }

    # Nếu user là cư dân (id_vaitro == 2), chỉ lấy hóa đơn của họ
    if request.user.vaitro_id == 2:
        khoanthu_filter['dot_thuphi__hoa_dons__id_hokhau__id_chuho'] = request.user
        hoadon_filter['id_hokhau__id_chuho'] = request.user
        tong_da_thu_filter['id_hokhau__id_chuho'] = request.user
        tong_can_thu_filter['id_hokhau__id_chuho'] = request.user

    phi_status = KhoanThu.objects.filter(
        **khoanthu_filter
    ).annotate(
        total_revenue=Sum("dot_thuphi__hoa_dons__da_dong")
    ).order_by("-total_revenue")[:7]

    pie_labels = [item.ten_khoanthu for item in phi_status]
    pie_data = [float(item.total_revenue) for item in phi_status]

    monthly_income = HoaDon.objects.filter(
        **hoadon_filter
    ).annotate(month=ExtractMonth("ngay_nop")).values(
        "month"
    ).annotate(total=Sum("da_dong")).order_by("month")

    line_labels = ["T1", "T2", "T3", "T4", "T5",
                   "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
    line_data = [0] * 12
    for item in monthly_income:
        if item["month"]:
            line_data[item["month"] - 1] = float(item["total"])

    tong_da_thu = HoaDon.objects.filter(
        **tong_da_thu_filter
    ).aggregate(Sum("da_dong"))["da_dong__sum"] or 0

    tong_can_thu = HoaDon.objects.filter(
        **tong_can_thu_filter
    ).aggregate(Sum("tong_tien"))["tong_tien__sum"] or 0

    phan_tram = round((float(tong_da_thu) / float(tong_can_thu))
                      * 100, 1) if tong_can_thu > 0 else 0

    context = {
        "pie_labels": json.dumps(pie_labels),
        "pie_data": json.dumps(pie_data),
        "line_labels": json.dumps(line_labels),
        "line_data": json.dumps(line_data),
        "tong_da_thu": tong_da_thu,
        "tong_can_thu": tong_can_thu,
        "phan_tram": phan_tram,
        "selected_year": year,
        "years": range(datetime.now().year - 1, datetime.now().year + 1),
    }
    return render(request, "core/Statistics.html", context)


@login_required(login_url="login")
def export_finance_excel(request):
    year_str = request.GET.get("year", str(timezone.now().year))
    try:
        year = int(year_str)
    except ValueError:
        year = timezone.now().year

    wb = Workbook()
    ws = wb.active
    ws.title = f"Thong ke {year}"

    bold_font = Font(bold=True, color="FFFFFF")
    center_align = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    header_fill = PatternFill(start_color="1976D2",
                              end_color="1976D2", fill_type="solid")

    ws.row_dimensions[1].height = 20
    ws.merge_cells("A1:D1")
    ws["A1"] = f"BÁO CÁO TÀI CHÍNH NĂM {year} - CHUNG CƯ BLUEMOON"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = center_align
    ws["A1"].alignment = Alignment(
        horizontal="center", vertical="center", wrap_text=True)

    headers = ["Tháng", "Số hóa đơn đã thanh toán",
               "Đã thanh toán (VND)"]
    ws.append([])
    ws.append(headers)

    for cell in ws[3]:
        cell.font = bold_font
        cell.fill = header_fill
        # cell.border = border
        cell.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True)

    all_invoices = HoaDon.objects.filter(
        (
            Q(id_dotthu__ngay_batdau__year=year) |
            Q(id_dotthu__ngay_ketthuc__year=year)
        ),
        is_deleted=False
    )
    paid_invoices = HoaDon.objects.filter(
        ngay_nop__year=year,
        is_deleted=False
    )
    # Nếu user là cư dân
    if request.user.vaitro_id == 2:
        all_invoices = all_invoices.filter(id_hokhau__id_chuho=request.user)
        paid_invoices = paid_invoices.filter(id_hokhau__id_chuho=request.user)

    # Group by month
    total_year_money = 0
    remaining_year_money = 0
    for m in range(1, 13):
        # Tổng số hóa đơn đã thanh toán
        count = all_invoices.filter(
            ngay_nop__month=m, ngay_nop__year=year).count()

        # Tổng số tiền phải thu
        total = all_invoices.filter(
            Q(id_dotthu__ngay_batdau__month=m) |
            Q(id_dotthu__ngay_ketthuc__month=m)
        ).aggregate(
            Sum("tong_tien"))["tong_tien__sum"] or 0

        # Tổng số tiền đã thanh toán
        paid = paid_invoices.filter(ngay_nop__month=m).aggregate(
            Sum("da_dong"))["da_dong__sum"] or 0
        total_year_money += paid

        remain = total - paid
        remaining_year_money += remain

        ws.append([f"Tháng {m}", count, paid])
        # ws.append([f"Tháng {m}", count, paid, remain])

    for idx, cell in enumerate(ws[ws.max_row], start=1):
        if idx == 1:
            cell.alignment = Alignment(horizontal="left")
        else:
            cell.alignment = Alignment(horizontal="right")

    ws.append(["Tổng", "", total_year_money])
    # ws.append(["Tổng", "", total_year_money, remaining_year_money])

    last_row = ws.max_row
    ws.cell(row=last_row, column=1).font = Font(bold=True)
    ws.cell(row=last_row, column=3).font = Font(bold=True)
    ws.cell(row=last_row, column=4).font = Font(bold=True)

    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 17
    ws.column_dimensions["D"].width = 27

    number_format = '#,##0'
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row, min_col=2, max_col=4):
        for cell in row:
            cell.number_format = number_format

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f"attachment; filename=BaoCao_BlueMoon_{year}.xlsx"
    wb.save(response)
    return response


@login_required(login_url="login")
def invoice_history(request):
    query = request.GET.get("search_invoice", "")
    selected_month = request.GET.get("month", "")
    selected_year = request.GET.get("year", "")
    dotthu_name = request.GET.get("dotthu_name", "")
    # "1" (đã đóng), "0" (chưa đóng), "" (tất cả)
    da_dong = request.GET.get("da_dong", "")

    invoice_list = HoaDon.objects.select_related(
        "id_hokhau", "id_dotthu").filter(is_deleted=False).order_by("-ngay_nop")

    # Nếu user là cư dân (id_vaitro == 2)
    if request.user.vaitro_id == 2:
        invoice_list = invoice_list.filter(id_hokhau__id_chuho=request.user)

    if query:
        invoice_list = invoice_list.filter(
            Q(id_hoadon__icontains=query) |
            Q(id_hokhau__id_canho__so_can_ho__icontains=query) |
            Q(id_dotthu__ten_dotthu__icontains=query)
        )

    today = timezone.now().date()

    if da_dong == "1":
        invoice_list = invoice_list.filter(da_dong__gt=0)
    elif da_dong == "0":
        invoice_list = invoice_list.filter(da_dong=0)
    elif da_dong == "-1":
        invoice_list = invoice_list.filter(
            da_dong=0,
            id_dotthu__ngay_ketthuc__lt=today
        )

    if selected_month:
        invoice_list = invoice_list.annotate(
            month=ExtractMonth("ngay_nop")).filter(month=selected_month)
    if selected_year:
        invoice_list = invoice_list.annotate(
            year=ExtractYear("ngay_nop")).filter(year=selected_year)

    for i in invoice_list:
        i.is_overdue = (
            i.id_dotthu.ngay_ketthuc < today
            and i.da_dong == 0
        )

    context = {
        "invoice_list": invoice_list,
        "query": query,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "dotthu_name": dotthu_name,
        "da_dong": da_dong,
        "years": range(2025, datetime.now().year + 1),
        "months": range(1, 13),
    }
    return render(request, "invoice/InvoiceHistory.html", context)


@login_required(login_url="login")
def view_invoice_detail_modal(request, pk):
    hoadon = get_object_or_404(
        HoaDon.objects.select_related("id_hokhau", "id_dotthu"),
        id_hoadon=pk,
    )
    # Nếu user là cư dân (id_vaitro == 2)
    if request.user.vaitro_id == 2:
        if getattr(hoadon.id_hokhau, 'id_chuho_id', None) != request.user.pk:
            return render(request, "core/message.html", {"error": "Bạn không có quyền xem hóa đơn này."})
    khoanthu_list = hoadon.id_dotthu.id_khoanthu.all()
    hoadon_chitiet_list = hoadon.chi_tiets.all()
    return render(request, "invoice/ViewInvoiceDetailModal.html", {
        "hoadon": hoadon,
        "khoanthu_list": khoanthu_list,
        "hoadon_chitiet_list": hoadon_chitiet_list,
    })


@login_required(login_url="login")
@role_required([3])
def delete_invoice_modal(request, pk):
    hoadon = get_object_or_404(HoaDon, id_hoadon=pk)

    if request.method == "POST":
        if hoadon.ngay_nop is None:
            hoadon.is_deleted = True
            if request.user.is_authenticated:
                hoadon.updated_by = str(request.user)
            hoadon.save(update_fields=["is_deleted",
                        "updated_by"])
            messages.success(request, f"Hóa đơn #{pk} đã được xóa thành công!")
            return redirect("invoice_history")
        else:
            messages.error(request, "Không thể xóa hóa đơn đã thanh toán!")
            return redirect("invoice_history")
    return render(request, "invoice/DeleteInvoiceModal.html", {"hoadon": hoadon})
