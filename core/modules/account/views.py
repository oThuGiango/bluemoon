from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from core.decorators import role_required
from django.contrib import messages

from core.forms import TaiKhoanEditForm, TaiKhoanForm

from .models import TaiKhoan, VaiTro


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

    context = {
        "tai_khoan_list": tai_khoan_list,
        "query": query,
        "status": status,
        "role": role,
    }

    return render(request, "account/AccountManage.html", context)


@login_required(login_url="login")
@role_required([1])
def delete_account(request, id_taikhoan):
    account = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)
    if request.method == "POST":
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
    if request.method == "POST":
        form = TaiKhoanForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            vaitro = form.cleaned_data["vaitro"]
            vaitro_obj = get_object_or_404(VaiTro, id_vaitro=vaitro)

        if not username or not password1 or not password2:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin!")
            return redirect("accountmanage")

        if password1 != password2:
            messages.error(request, "Mật khẩu không khớp")
            return redirect("accountmanage")

        if TaiKhoan.objects.filter(username=username).exists():
            messages.error(request, "Tên tài khoản này đã tồn tại!")
            return redirect("accountmanage")

        TaiKhoan.objects.create(
            username=username,
            password=make_password(password1),
            vaitro=vaitro_obj,
            is_active=True,
            is_staff=False,
            create_by=request.user.username if request.user.is_authenticated else "Unknown",
            create_at=timezone.now(),
        )
        messages.success(request, "Thêm tài khoản thành công!")
        return redirect("accountmanage")

    form = TaiKhoanForm()
    return render(request, "account/AccountAdd.html", {"form": form})


@login_required(login_url="login")
@role_required([1])
def view_account(request, pk):
    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=pk)
    return render(request, "account/AccDetailModal.html", {"taikhoan": taikhoan})


@login_required(login_url="login")
@role_required([1])
def edit_account(request, id_taikhoan):
    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)

    if request.method == "POST":
        form = TaiKhoanEditForm(request.POST, instance=taikhoan)
        username = form.data.get("username")
        vaitro_id = form.data.get("vaitro")
        try:
            vaitro = VaiTro.objects.get(id_vaitro=vaitro_id)
            taikhoan.vaitro = vaitro    
        except VaiTro.DoesNotExist:
            messages.error(request, "Vai trò không tồn tại!")
            return redirect("accountmanage")
                    
        if not TaiKhoan.objects.filter(username=username).exists():
            taikhoan.username = username
        else:
            messages.error(request, "Tên tài khoản này đã tồn tại!")
            return redirect("accountmanage")
            
        if form.is_valid():
            taikhoan.updated_by = request.user.username
            taikhoan.updated_at = timezone.now()

            taikhoan.save()
            
            messages.success(request, "Thay đổi thông tin thành công!")
            return redirect("accountmanage")
    
    form = TaiKhoanEditForm(instance=taikhoan)
    context = {
        "form": form,
        "taikhoan": taikhoan,
    }
    return render(request, "account/ChangeAccount.html", context)
