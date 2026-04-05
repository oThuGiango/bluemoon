import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from core.forms import DotThuPhiForm, KhoanThuForm
from core.modules.resident.models import HoKhau
from .models import DotThuPhi, HoaDon, KhoanThu


@login_required(login_url="login")
def fee_management(request):
    query = request.GET.get("search_khoanthu")
    khoan_thu_list = KhoanThu.objects.all()

    if query:
        khoan_thu_list = khoan_thu_list.filter(
            Q(ten_khoanthu__icontains=query) | Q(id_khoanthu__icontains=query))
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
    return render(request, "core/ViewFeeDetailModal.html", {"khoan_thu": khoan_thu})


@login_required(login_url="login")
def add_khoanthu(request):
    if request.method == "POST":
        form = KhoanThuForm(request.POST)
        if form.is_valid():
            new_id = form.cleaned_data.get("id_khoanthu")
            if KhoanThu.objects.filter(id_khoanthu=new_id).exists():
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"error": "Mã khoản thu này đã tồn tại!"}, status=400)
                messages.error(request, "Mã khoản thu này đã tồn tại!")
                return render(request, "core/AddFeeModal.html", {"form": form})

            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})
            messages.success(request, "Thêm khoản thu thành công!")
            return redirect("fee_management")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"error": "Dữ liệu không hợp lệ!"}, status=400)
    else:
        form = KhoanThuForm()
    return render(request, "core/AddFeeModal.html", {"form": form})


@login_required(login_url="login")
def edit_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)

    if request.method == "POST":
        form = KhoanThuForm(request.POST, instance=khoan_thu)

        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})
            messages.success(
                request, f"Khoản thu '{khoan_thu.ten_khoanthu}' đã được cập nhật thành công!")
            return redirect("fee_management")
        else:
            context = {"form": form, "khoan_thu": khoan_thu}
            return render(request, "core/EditFeeModal.html", context, status=400)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = KhoanThuForm(instance=khoan_thu)
        context = {"form": form, "khoan_thu": khoan_thu}
        return render(request, "core/EditFeeModal.html", context)
    else:
        form = KhoanThuForm(instance=khoan_thu)
        context = {
            "form": form,
            "khoan_thu": khoan_thu,
            "page_title": f"CHỈNH SỬA KHOẢN THU - {khoan_thu.ten_khoanthu}",
        }
        return render(request, "core/EditFee.html", context)


@login_required(login_url="login")
def delete_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)

    if request.method == "POST":
        khoan_thu.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Khoản thu đã được xóa thành công!"})
        return redirect("fee_management")
    return render(request, "core/DeleteFeeModal.html", {"khoan_thu": khoan_thu})


@login_required(login_url="login")
def fee_collection_period(request):
    query = request.GET.get("search_dotthu")
    dot_thu_phi_list = DotThuPhi.objects.select_related("id_khoanthu").all()
    active_count = dot_thu_phi_list.filter(trang_thai="open").count()
    if query:
        dot_thu_phi_list = dot_thu_phi_list.filter(
            Q(ten_dotthu__icontains=query) | Q(id_dotthu__icontains=query))
    context = {
        "dot_thu_phi_list": dot_thu_phi_list,
        "active_count": active_count,
        "query": query,
    }
    return render(request, "core/FeeCollectionPeriod.html", context)


@login_required(login_url="login")
def view_dotthu_detail_modal(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    danh_sach_hoa_don = dot_thu.hoa_dons.select_related(
        "id_hokhau").all().order_by("id_hokhau__so_can_ho")
    ids_da_co = danh_sach_hoa_don.values_list("id_hokhau_id", flat=True)
    tat_ca_ho_khau = HoKhau.objects.exclude(id_hokhau__in=ids_da_co)
    context = {
        "dot_thu": dot_thu,
        "danh_sach_hoa_don": danh_sach_hoa_don,
        "tat_ca_ho_khau": tat_ca_ho_khau,
    }
    return render(request, "core/ViewPeriodDetailModal.html", context)


@login_required(login_url="login")
def update_payment_status(request):
    invoice_ids = request.POST.getlist("invoice_ids[]")

    if not invoice_ids:
        return JsonResponse({"status": "error", "message": "Không có hóa đơn nào được chọn"}, status=400)

    try:
        HoaDon.objects.filter(id_hoadon__in=invoice_ids, ngay_nop__isnull=True).update(
            ngay_nop=timezone.now())
        return JsonResponse({"status": "success", "message": "Cập nhật trạng thái thành công"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required(login_url="login")
def create_invoices_for_period(request):
    id_dotthu = request.POST.get("id_dotthu")
    hokhau_ids = request.POST.getlist("hokhau_ids[]")
    multipliers = request.POST.getlist("multipliers[]")
    prices = request.POST.getlist("prices[]")

    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=id_dotthu)
    last_invoice = HoaDon.objects.all().order_by("id_hoadon").last()
    next_id = (last_invoice.id_hoadon + 1) if last_invoice else 1

    for hk_id, mult, price in zip(hokhau_ids, multipliers, prices):
        hokhau = get_object_or_404(HoKhau, id_hokhau=hk_id)

        if not HoaDon.objects.filter(id_dotthu=dot_thu, id_hokhau=hokhau).exists():
            final_amount = float(price) * float(mult)

            HoaDon.objects.create(
                id_hoadon=next_id,
                id_dotthu=dot_thu,
                id_hokhau=hokhau,
                tong_tien=final_amount,
            )
            next_id += 1
    danh_sach_hoa_don = dot_thu.hoa_dons.select_related(
        "id_hokhau").all().order_by("id_hokhau__so_can_ho")
    tat_ca_ho_khau = HoKhau.objects.exclude(
        id_hokhau__in=danh_sach_hoa_don.values_list("id_hokhau_id", flat=True))

    return render(
        request,
        "core/ViewPeriodDetailModal.html",
        {
            "dot_thu": dot_thu,
            "danh_sach_hoa_don": danh_sach_hoa_don,
            "tat_ca_ho_khau": tat_ca_ho_khau,
        },
    )


@login_required(login_url="login")
def add_dotthu(request):
    if request.method == "POST":
        form = DotThuPhiForm(request.POST)
        if form.is_valid():
            new_id = form.cleaned_data.get("id_dotthu")
            if DotThuPhi.objects.filter(id_dotthu=new_id).exists():
                return JsonResponse({"error": "Mã đợt thu phí này đã tồn tại!"}, status=400)

            form.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})

            return redirect("fee_collection_period")
    else:
        form = DotThuPhiForm()
    return render(request, "core/AddPeriodModal.html", {"form": form})


@login_required(login_url="login")
def edit_dotthu(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    if request.method == "POST":
        form = DotThuPhiForm(request.POST, instance=dot_thu)
        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})
            return redirect("fee_collection_period")
        else:
            return render(request, "core/EditPeriodModal.html", {"form": form, "dot_thu": dot_thu}, status=400)

    form = DotThuPhiForm(instance=dot_thu)
    return render(request, "core/EditPeriodModal.html", {"form": form, "dot_thu": dot_thu})


@login_required(login_url="login")
def delete_dotthu(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    if request.method == "POST":
        dot_thu.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Đợt thu phí đã được xóa thành công!"})
        return redirect("fee_collection_period")
    return render(request, "core/DeletePeriodModal.html", {"dot_thu": dot_thu})


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
        "id_hokhau", "id_dotthu").all().order_by("-ngay_nop")
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
    return render(request, "core/InvoiceHistory.html", context)


@login_required(login_url="login")
def view_invoice_detail_modal(request, pk):
    hoadon = get_object_or_404(
        HoaDon.objects.select_related("id_hokhau", "id_dotthu__id_khoanthu"),
        id_hoadon=pk,
    )
    return render(request, "core/ViewInvoiceDetailModal.html", {"hoadon": hoadon})


@login_required(login_url="login")
def delete_invoice_modal(request, pk):
    hoadon = get_object_or_404(HoaDon, id_hoadon=pk)

    if request.method == "POST":
        if hoadon.ngay_nop is None:
            hoadon.delete()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success", "message": f"Hóa đơn #{pk} đã được xóa thành công!"})
            return redirect("invoice_history")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "Không thể xóa hóa đơn đã thanh toán!"}, status=400)
            return redirect("invoice_history")
    return render(request, "core/DeleteInvoiceModal.html", {"hoadon": hoadon})
