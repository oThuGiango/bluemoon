from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from core.decorators import role_required
from core.modules.account.models import TaiKhoan
from core.modules.apartment.models import CanHo
from core.modules.resident.models import HoKhau, NhanKhau
from core.modules.fee.models import KhoanThu, HoaDon, DotThuPhi


@login_required(login_url="login")
def home(request):
    user = request.user

    if user.is_authenticated:
        if user.is_superuser:
            return render(request, "core/homepage.html")
        if user.vaitro.id_vaitro == 1:
            return redirect("admin_home")
        if user.vaitro.id_vaitro == 3:
            accountant_home(request)

    return render(request, "core/homepage.html")


def user_logout(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def profile(request):
    user = request.user

    if user.is_authenticated:
        if user.is_superuser:
            return render(request, "account/profile.html", {"user": user})
        id_vaitro = user.vaitro.id_vaitro
        if id_vaitro is not None:
            return render(request, "account/profile.html", {"user": user})

    return render(request, "core/message.html", {"error": "Bạn chưa đăng nhập"})


def login_view(request):
    if request.method == "POST":
        username_request = request.POST.get("username")
        password_request = request.POST.get("password")

        user = authenticate(request, username=username_request,
                            password=password_request)
        print(username_request + "\n" + password_request)
        if user is not None:
            if not user.is_active or user.is_deleted:
                return render(
                    request,
                    "core/login.html",
                    {"error": "Tài khoản của bạn đã bị vô hiệu hóa"},
                )

            login(request, user)
            if request.user.is_superuser:
                return redirect("home")

            id_vaitro = request.user.vaitro.id_vaitro
            if id_vaitro is not None:
                if id_vaitro == 1:
                    return redirect("admin_home")
                if id_vaitro == 3:
                    return redirect("accountant_home")
                else:
                    return redirect("home")
        else:
            return render(
                request,
                "core/login.html",
                {"error": "Sai tên đăng nhập hoặc mật khẩu"},
            )

    return render(request, "core/login.html")


@login_required(login_url="login")
@role_required([1])
def admin_home(request):
    total_accounts = TaiKhoan.objects.filter(is_deleted=False, is_active=True).count()
    total_apartments = CanHo.objects.filter(is_deleted=False).count()
    total_residents = NhanKhau.objects.filter(
        is_deleted=False,
        is_active=True,
    ).count()

    context = {
        "total_accounts": total_accounts,
        "total_apartments": total_apartments,
        "total_residents": total_residents,
    }
    return render(request, "core/admin_home.html", context)


@login_required(login_url="login")
@role_required([3])
def accountant_home(request):
    current_year = timezone.now().year

    context = {
        "total_khoanthu": KhoanThu.objects.filter(is_deleted=False).count(),
        "total_nhankhau": NhanKhau.objects.filter(
            is_deleted=False,
            is_active=True,
        ).count(),
        "total_hoadon": HoaDon.objects.filter(
            is_deleted=False,
            created_at__year=current_year,
        ).count(),
        "total_dotthu": DotThuPhi.objects.filter(
            is_deleted=False,
            created_at__year=current_year,
        ).count(),
    }
    return render(request, "core/Accountant.html", context)


def test(request):
    ds_ho_khau = HoKhau.objects.all()
    return render(request, "core/test.html", {"ho_khau_list": ds_ho_khau})
