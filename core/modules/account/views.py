from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render

from .models import TaiKhoan, VaiTro


@login_required(login_url="login")
def accountmanage(request):
    tai_khoan_list = TaiKhoan.objects.all()
    query = request.GET.get("search_id", "")
    user = request.user
    print(user.is_authenticated)
    if user.is_authenticated:
        id_vaitro = request.user.vaitro.id_vaitro
        if id_vaitro is not None:
            if id_vaitro == 1:
                if query:
                    try:
                        for a in tai_khoan_list:
                            if a.id_taikhoan == int(query):
                                tai_khoan_list = [a]
                    except ValueError:
                        tai_khoan_list = TaiKhoan.objects.all()

                context = {
                    "tai_khoan_list": tai_khoan_list,
                    "query": query,
                }

                return render(request, "core/accountmanage.html", context)
    return render(request, "core/message.html", {"error": "Bạn không có quyền truy cập trang này"})


@login_required(login_url="login")
def accountmanage_delete(request, id_taikhoan):
    exists = TaiKhoan.objects.filter(id_taikhoan=id_taikhoan).exists()
    if exists:
        account = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)
        account.is_deleted = True
    return render(request, "core/accountmanage_delete.html")


@login_required(login_url="login")
def accountmanage_addaccount(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        vaitro_string = request.POST.get("vaitro")
        match vaitro_string:
            case "admin":
                vaitro = get_object_or_404(VaiTro, id_vaitro=1)
        match vaitro_string:
            case "user":
                vaitro = get_object_or_404(VaiTro, id_vaitro=2)
        match vaitro_string:
            case "ketoan":
                vaitro = get_object_or_404(VaiTro, id_vaitro=3)

        if not username or not password1 or not password2:
            return render(request, "core/accountmanage_addaccount.html", {"error": "Vui lòng nhập đầy đủ thông tin."})

        if password1 != password2:
            return render(request, "core/accountmanage_addaccount.html", {"error": "Mật khẩu không khớp"})

        if TaiKhoan.objects.filter(username=username).exists():
            return render(request, "core/accountmanage_addaccount.html", {"error": "Tên đăng nhập đã tồn tại "})

        TaiKhoan.objects.create(
            username=username,
            password=make_password(password1),
            vaitro=vaitro,
            is_active=True,
            is_staff=False,
        )

    return render(request, "core/accountmanage_addaccount.html", {"error": "Tạo tài khoản thành công "})


@login_required(login_url="login")
def view_taikhoan(request, id_taikhoan):
    user = authenticate(request, username="admin", password="2005")
    login(request, user)

    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)
    return render(request, "core/accountmanage_view.html", {"taikhoan": taikhoan})


@login_required(login_url="login")
def edit_taikhoan(request, id_taikhoan):
    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)

    if request.method == "POST":
        username = request.POST.get("username")
        password_raw = request.POST.get("password")
        vaitro_id = request.POST.get("vaitro_id")
        try:
            vaitro = VaiTro.objects.get(id_vaitro=vaitro_id)
            taikhoan.vaitro = vaitro
        except VaiTro.DoesNotExist:
            return render(request, "core/message.html", {"error": "ID vai trò không tồn tại"})
        if taikhoan.username != username:
            if not TaiKhoan.objects.filter(username=username).exists():
                taikhoan.username = username
            else:
                return render(request, "core/message.html", {"error": "username này đã tồn tại"})

        taikhoan.set_password(password_raw)

        taikhoan.save()
        return render(request, "core/message.html", {"error": "Thay đổi thông tin thành công"})
    return render(request, "core/accountmanage_change.html", {"taikhoan": taikhoan})
