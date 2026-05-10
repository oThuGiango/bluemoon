from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from core.decorators import role_required
from django.contrib import messages

from core.forms import TaiKhoanEditForm, TaiKhoanForm

from .models import TaiKhoan, VaiTro
from core.modules.resident.models import CanHo,  HoKhau
from core.modules.fee.models import HoaDon


@login_required(login_url="login")
@role_required([1])
def accountmanage(request):
    tai_khoan_list = TaiKhoan.objects.filter(
        is_deleted=False).order_by("-id_taikhoan")

    query = request.GET.get("search_id", "")
    status = request.GET.get('status')
    role = request.GET.get('role')

    if status in ['0', '1']:
        tai_khoan_list = tai_khoan_list.filter(is_active=(status == '1'))
    if role in ['1', '2', '3']:
        tai_khoan_list = tai_khoan_list.filter(vaitro__id_vaitro=role)

    if query:
        tai_khoan_list = tai_khoan_list.filter(
            (Q(username__icontains=query) | Q(
                id_taikhoan__icontains=query))
        )

    total_count = tai_khoan_list.count()
    context = {
        "tai_khoan_list": tai_khoan_list,
        "query": query,
        "status": status,
        "role": role,
        "total_count": total_count,
    }

    return render(request, "account/AccountManage.html", context)


@login_required(login_url="login")
@role_required([1])
def delete_account(request, id_taikhoan):
    account = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)
    if request.method == "POST":
        has_hokhau = HoKhau.objects.filter(
            id_chuho=account, is_deleted=False).exists()
        has_hoadon = HoaDon.objects.filter(
            id_hokhau__id_chuho=account, is_deleted=False).exists()
        if has_hokhau or has_hoadon:
            messages.error(
                request, "Không thể xóa tài khoản vì còn hộ khẩu hoặc hóa đơn liên kết!")
            return redirect("accountmanage")

        account.is_deleted = True
        account.updated_at = timezone.now()
        account.updated_by = str(request.user)
        account.save(
            update_fields=["is_deleted", "updated_at", "updated_by"])
        messages.success(request, "Tài khoản đã được xóa thành công!")
        return redirect("accountmanage")

    return render(request, "account/DeleteAccount.html", {"account": account})


@login_required(login_url="login")
@role_required([1])
def add_account(request):
    # Lấy các căn hộ chưa có hộ khẩu hoặc hộ khẩu đã bị xóa/deactive
    canho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_canho__isnull=False).values_list('id_canho', flat=True)
    available_canho = CanHo.objects.filter(is_deleted=False).exclude(
        id_canho__in=canho_with_active_hokhau)

    if request.method == "POST":
        form = TaiKhoanForm(request.POST, available_canho=available_canho)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            vaitro = form.cleaned_data["vaitro"]
            resident_status = form.cleaned_data.get("resident_status")
            vaitro_obj = get_object_or_404(VaiTro, id_vaitro=vaitro)
        else:
            form = TaiKhoanForm(available_canho=available_canho)
            return render(request, "account/AccountAdd.html", {"form": form, "available_canho": available_canho})

        if not username or not password1 or not password2:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin!")
            return redirect("accountmanage")

        if password1 != password2:
            messages.error(request, "Mật khẩu không khớp")
            return redirect("accountmanage")

        if TaiKhoan.objects.filter(username=username).exists():
            messages.error(request, "Tên tài khoản này đã tồn tại!")
            return redirect("accountmanage")

        new_account = TaiKhoan.objects.create(
            username=username,
            password=make_password(password1),
            vaitro=vaitro_obj,
            is_active=True,
            is_staff=False,
            create_by=request.user.username if request.user.is_authenticated else "Unknown",
            create_at=timezone.now(),
        )
        # Nếu có chọn căn hộ, tạo hộ khẩu mới cho chủ hộ này
        id_canho = request.POST.get("id_canho")
        if id_canho and vaitro_obj.id_vaitro == 2:
            canho = get_object_or_404(CanHo, id_canho=id_canho)
            HoKhau.objects.create(
                id_canho=canho,
                id_chuho=new_account,
                resident_status=resident_status,
                updated_by=request.user.username if request.user.is_authenticated else None
            )

        messages.success(request, "Thêm tài khoản thành công!")
        return redirect("accountmanage")

    form = TaiKhoanForm(available_canho=available_canho)
    return render(request, "account/AccountAdd.html", {"form": form, "available_canho": available_canho})


@login_required(login_url="login")
@role_required([1])
def view_account(request, pk):
    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=pk)
    # Lấy danh sách các căn hộ mà tài khoản này đang là chủ hộ
    hokhau_list = HoKhau.objects.filter(
        id_chuho=taikhoan, is_deleted=False, is_active=True)
    canho_names = list(hokhau_list.values_list(
        'id_canho__so_can_ho', flat=True))
    return render(request, "account/AccDetailModal.html", {"taikhoan": taikhoan, "canho_names": canho_names})


@login_required(login_url="login")
@role_required([1])
def edit_account(request, id_taikhoan):
    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)
    # Lấy hộ khẩu hiện tại của tài khoản (nếu có)
    hokhau = HoKhau.objects.filter(
        id_chuho=taikhoan, is_deleted=False, is_active=True).first()
    # Lấy các căn hộ chưa có hộ khẩu active (trừ căn hộ hiện tại nếu có)
    canho_with_active_hokhau = HoKhau.objects.filter(
        is_deleted=False, is_active=True, id_canho__isnull=False).values_list('id_canho', flat=True)
    available_canho = CanHo.objects.filter(is_deleted=False).exclude(
        id_canho__in=canho_with_active_hokhau)
    if hokhau and hokhau.id_canho:
        available_canho = available_canho | CanHo.objects.filter(
            id_canho=hokhau.id_canho.id_canho)

    if request.method == "POST":
        form = TaiKhoanEditForm(
            request.POST, instance=taikhoan, available_canho=available_canho)
        username = form.data.get("username")
        vaitro_id = form.data.get("vaitro")
        resident_status = form.data.get("resident_status")
        try:
            vaitro = VaiTro.objects.get(id_vaitro=vaitro_id)
            taikhoan.vaitro = vaitro
        except VaiTro.DoesNotExist:
            messages.error(request, "Vai trò không tồn tại!")
            return redirect("accountmanage")

        if not TaiKhoan.objects.filter(username=username).exclude(id_taikhoan=taikhoan.id_taikhoan).exists():
            taikhoan.username = username
        else:
            messages.error(request, "Tên tài khoản này đã tồn tại!")
            return redirect("accountmanage")

        if form.is_valid():
            taikhoan.updated_by = request.user.username
            taikhoan.updated_at = timezone.now()
            taikhoan.save()
            # Xử lý cập nhật hộ khẩu nếu có chọn lại căn hộ hoặc tình trạng cư trú
            id_canho = request.POST.get("id_canho")
            if id_canho and taikhoan.vaitro_id == 2:
                canho = get_object_or_404(CanHo, id_canho=id_canho)
                if hokhau:
                    hokhau.id_canho = canho
                    hokhau.resident_status = resident_status
                    hokhau.updated_by = request.user.username if request.user.is_authenticated else None
                    hokhau.save()
                else:
                    HoKhau.objects.create(
                        id_canho=canho,
                        id_chuho=taikhoan,
                        resident_status=resident_status,
                        updated_by=request.user.username if request.user.is_authenticated else "Unknown"
                    )
            elif hokhau and resident_status:
                hokhau.resident_status = resident_status
                hokhau.updated_by = request.user.username if request.user.is_authenticated else None
                hokhau.save()
            messages.success(request, "Thay đổi thông tin thành công!")
            return redirect("accountmanage")

    form = TaiKhoanEditForm(instance=taikhoan, available_canho=available_canho)
    context = {
        "form": form,
        "taikhoan": taikhoan,
        "available_canho": available_canho.distinct(),
        "hokhau": hokhau,
    }
    return render(request, "account/ChangeAccount.html", context)


@login_required(login_url="login")
@role_required([1])
def deactivate_account(request, pk):
    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=pk)
    if request.method == "POST":
        new_status = not taikhoan.is_active
        # Nếu muốn active lại tài khoản, kiểm tra điều kiện hộ khẩu
        if new_status:
            hokhau_list = HoKhau.objects.filter(
                id_chuho=taikhoan, is_deleted=False)
            for hokhau in hokhau_list:
                if hokhau.id_canho:
                    # Có hộ khẩu active khác cùng căn hộ?
                    exists = HoKhau.objects.filter(
                        id_canho=hokhau.id_canho,
                        is_deleted=False,
                        is_active=True
                    ).exclude(id_hokhau=hokhau.id_hokhau).exists()
                    if exists:
                        canho_name = hokhau.id_canho.so_can_ho if hasattr(
                            hokhau.id_canho, 'so_can_ho') else str(hokhau.id_canho)
                        messages.error(
                            request, f"Không thể kích hoạt tài khoản vì căn hộ '{canho_name}' đã có hộ khẩu mới!")
                        return redirect("accountmanage")
        taikhoan.is_active = new_status
        taikhoan.updated_at = timezone.now()
        taikhoan.updated_by = str(request.user)
        taikhoan.save(update_fields=["is_active", "updated_at", "updated_by"])
        # Đồng bộ trạng thái is_active của các hộ khẩu với tài khoản
        HoKhau.objects.filter(id_chuho=taikhoan, is_deleted=False).update(
            is_active=taikhoan.is_active)
        if taikhoan.is_active:
            messages.success(
                request, f"Tài khoản '{taikhoan.username}' đã được kích hoạt!")
        else:
            messages.success(
                request, f"Tài khoản '{taikhoan.username}' đã được vô hiệu hóa!")
        return redirect("accountmanage")
    return redirect("accountmanage")
