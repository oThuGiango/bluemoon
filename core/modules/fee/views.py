import json
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
        for kt in khoanthu_objs:
            if kt.don_vi_tinh == "dientich":
                so_luong = float(getattr(hokhau, "dien_tich", 0) or 0)
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
            "tong": tong, "chi_tiet": chi_tiet, "so_can_ho": hokhau.so_can_ho}
        tong_tien_dot += tong
    return tong_tien_ho, tong_tien_dot


@login_required(login_url="login")
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
def view_khoanthu_detail_modal(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        pass
    return render(request, "fee/ViewFeeDetailModal.html", {"khoan_thu": khoan_thu})


@login_required(login_url="login")
def add_khoanthu(request):
    if request.method == "POST":
        form = KhoanThuForm(request.POST)
        if form.is_valid():
            ten_khoanthu = form.cleaned_data.get("ten_khoanthu").strip()
            if KhoanThu.objects.filter(ten_khoanthu__iexact=ten_khoanthu).exists():
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"error": "Tên khoản thu này đã tồn tại!"}, status=400)
                messages.error(request, "Tên khoản thu này đã tồn tại!")
                return render(request, "fee/AddFeeModal.html", {"form": form})

            khoan_thu = form.save(commit=False)
            # if not khoan_thu.phi_bat_buoc:
            #     khoan_thu.don_gia = 1
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
def delete_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)

    if request.method == "POST":
        khoan_thu.is_deleted = True
        khoan_thu.updated_at = timezone.now()
        if request.user.is_authenticated:
            khoan_thu.updated_by = str(request.user)
        khoan_thu.save(
            update_fields=["is_deleted", "updated_at", "updated_by"])
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Khoản thu đã được xóa thành công!"})
        return redirect("fee_management")
    return render(request, "fee/DeleteFeeModal.html", {"khoan_thu": khoan_thu})


@login_required(login_url="login")
def fee_collection_period(request):
    query = request.GET.get("search_dotthu")
    dot_thu_phi_list = DotThuPhi.objects.prefetch_related(
        "id_khoanthu").filter(is_deleted=False)
    active_count = dot_thu_phi_list.filter(
        trang_thai="open", is_deleted=False).count()
    if query:
        dot_thu_phi_list = dot_thu_phi_list.filter(
            (Q(ten_dotthu__icontains=query) | Q(
                id_dotthu__icontains=query)) & Q(is_deleted=False)
        )
    context = {
        "dot_thu_phi_list": dot_thu_phi_list,
        "active_count": active_count,
        "query": query,
    }
    return render(request, "period/FeeCollectionPeriod.html", context)


# Trang chi tiết đợt thu phí (page, không phải modal)
@login_required(login_url="login")
def fee_collection_period_detail(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    danh_sach_hoa_don = dot_thu.hoa_dons.select_related(
        "id_hokhau").filter(is_deleted=False).order_by("id_hokhau__so_can_ho")
    ids_da_co = danh_sach_hoa_don.values_list("id_hokhau_id", flat=True)
    tat_ca_ho_khau = HoKhau.objects.exclude(id_hokhau__in=ids_da_co)
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
def update_payment_status(request):
    invoice_ids = request.POST.getlist("invoice_ids[]")

    if not invoice_ids:
        return JsonResponse({"status": "error", "message": "Không có hóa đơn nào được chọn"}, status=400)

    try:
        # Lấy các hóa đơn cần cập nhật
        invoices = HoaDon.objects.filter(
            id_hoadon__in=invoice_ids, ngay_nop__isnull=True)
        for invoice in invoices:
            invoice.ngay_nop = timezone.now()
            invoice.da_dong = invoice.tong_tien
            invoice.save(update_fields=["ngay_nop", "da_dong"])
        return JsonResponse({"status": "success", "message": "Cập nhật trạng thái thành công"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required(login_url="login")
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

        if not created and getattr(hoadon, "is_deleted", False):
            hoadon.is_deleted = False
            hoadon.save(update_fields=["is_deleted"])

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
        "id_hokhau").all().order_by("id_hokhau__so_can_ho")
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
            instance.save()
            form.save_m2m()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})

            return redirect("fee_collection_period")
    else:
        form = DotThuPhiForm()
    return render(request, "period/AddPeriodModal.html", {"form": form})


@login_required(login_url="login")
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
                field for field in ["ten_dotthu", "ngay_batdau", "ngay_ketthuc", "trang_thai", "updated_at", "updated_by"] if hasattr(dot_thu, field)
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
def delete_dotthu(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    if request.method == "POST":
        dot_thu.is_deleted = True
        dot_thu.updated_at = timezone.now()
        if request.user.is_authenticated:
            dot_thu.updated_by = str(request.user)
        dot_thu.save(update_fields=["is_deleted", "updated_at", "updated_by"])
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Đợt thu phí đã được xóa thành công!"})
        return redirect("fee_collection_period")
    return render(request, "period/DeletePeriodModal.html", {"dot_thu": dot_thu})


@login_required(login_url="login")
def statistics_view(request):
    year_str = request.GET.get("year", str(datetime.now().year))
    try:
        year = int(year_str)
    except ValueError:
        year = datetime.now().year

    phi_status = KhoanThu.objects.filter(dot_thuphi__hoa_dons__ngay_nop__year=year).annotate(
        total_revenue=Sum("dot_thuphi__hoa_dons__tong_tien")
    ).order_by("-total_revenue")[:5]

    pie_labels = [item.ten_khoanthu for item in phi_status]
    pie_data = [float(item.total_revenue) for item in phi_status]

    monthly_income = HoaDon.objects.filter(ngay_nop__year=year).annotate(month=ExtractMonth("ngay_nop")).values(
        "month"
    ).annotate(total=Sum("tong_tien")).order_by("month")

    line_labels = ["T1", "T2", "T3", "T4", "T5",
                   "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
    line_data = [0] * 12
    for item in monthly_income:
        if item["month"]:
            line_data[item["month"] - 1] = float(item["total"])

    tong_da_thu = HoaDon.objects.filter(ngay_nop__year=year).aggregate(
        Sum("tong_tien"))["tong_tien__sum"] or 0

    so_ho = HoKhau.objects.filter(is_active=True).count()
    dot_thus = DotThuPhi.objects.filter(ngay_batdau__year=year)
    tong_can_thu = 0
    for dot in dot_thus:
        tong_can_thu += float(dot.id_khoanthu.don_gia) * so_ho

    phan_tram = round((float(tong_da_thu) / tong_can_thu)
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

    ws.merge_cells("A1:C1")
    ws["A1"] = f"BÁO CÁO TÀI CHÍNH NĂM {year} - CHUNG CƯ BLUEMOON"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = center_align

    headers = ["Tháng", "Số lượng hóa đơn", "Doanh thu thực tế (VND)"]
    ws.append([])
    ws.append(headers)

    for cell in ws[3]:
        cell.font = bold_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = border

    monthly_data = (
        HoaDon.objects.filter(ngay_nop__year=year)
        .annotate(month=ExtractMonth("ngay_nop"))
        .values("month")
        .annotate(count=Count("id_hoadon"), total=Sum("tong_tien"))
        .order_by("month")
    )

    total_year_money = 0
    for m in range(1, 13):
        data = next(
            (item for item in monthly_data if item["month"] == m), None)
        count = data["count"] if data else 0
        money = float(data["total"]) if data else 0
        total_year_money += money

        ws.append([f"Tháng {m}", count, money])
        for cell in ws[ws.max_row]:
            cell.border = border
            cell.alignment = Alignment(horizontal="right") if isinstance(
                cell.value, (int, float)) else center_align

    ws.append(["TỔNG CỘNG", "", total_year_money])
    last_row = ws.max_row
    ws.cell(row=last_row, column=1).font = Font(bold=True)
    ws.cell(row=last_row, column=3).font = Font(bold=True)
    for cell in ws[last_row]:
        cell.border = border

    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 25

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
    invoice_list = HoaDon.objects.select_related(
        "id_hokhau", "id_dotthu").filter(is_deleted=False).order_by("-ngay_nop")
    if query:
        invoice_list = invoice_list.filter(
            Q(id_hoadon__icontains=query) | Q(id_hokhau__so_can_ho__icontains=query))

    if selected_month:
        invoice_list = invoice_list.annotate(
            month=ExtractMonth("ngay_nop")).filter(month=selected_month)
    if selected_year:
        invoice_list = invoice_list.annotate(
            year=ExtractYear("ngay_nop")).filter(year=selected_year)
    context = {
        "invoice_list": invoice_list,
        "query": query,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "years": range(2020, datetime.now().year + 1),
        "months": range(1, 13),
    }
    return render(request, "invoice/InvoiceHistory.html", context)


@login_required(login_url="login")
def view_invoice_detail_modal(request, pk):
    hoadon = get_object_or_404(
        HoaDon.objects.select_related("id_hokhau", "id_dotthu"),
        id_hoadon=pk,
    )
    khoanthu_list = hoadon.id_dotthu.id_khoanthu.all()
    hoadon_chitiet_list = hoadon.chi_tiets.all()
    return render(request, "invoice/ViewInvoiceDetailModal.html", {
        "hoadon": hoadon,
        "khoanthu_list": khoanthu_list,
        "hoadon_chitiet_list": hoadon_chitiet_list,
    })


@login_required(login_url="login")
def delete_invoice_modal(request, pk):
    hoadon = get_object_or_404(HoaDon, id_hoadon=pk)

    if request.method == "POST":
        if hoadon.ngay_nop is None:
            hoadon.is_deleted = True
            hoadon.save(update_fields=["is_deleted"])
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success", "message": f"Hóa đơn #{pk} đã được xóa thành công!"})
            return redirect("invoice_history")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "Không thể xóa hóa đơn đã thanh toán!"}, status=400)
            return redirect("invoice_history")
    return render(request, "invoice/DeleteInvoiceModal.html", {"hoadon": hoadon})
