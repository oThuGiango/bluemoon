import json
from unicodedata import decimal
from django.http import HttpResponse, JsonResponse
from calendar import day_name
from pyexpat.errors import messages
from django.db import transaction

from webbrowser import get
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReservationForm, KhoanThuForm, DotThuPhiForm
from .models import HoKhau, LoaiBienDong, NhanKhau, TaiKhoan, VaiTro, KhoanThu, DotThuPhi, HoaDon, BienDongNhanKhau
from datetime import datetime, timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.contrib.auth.hashers import make_password
from django.db.models.functions import ExtractMonth, ExtractYear
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from django.utils import timezone
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


@login_required(login_url="login")
def home(request):
    user = request.user

    if user.is_authenticated:
        if user.is_superuser:
            return render(request, 'core/homepage.html')
        if user.vaitro.id_vaitro == 1:
            admin_home(request)
        if user.vaitro.id_vaitro == 3:
            accountant_home(request)
    
    return render(request, 'core/mainpage.html')



def user_logout(request):
    logout(request)
#    messages.success(request, "Bạn đã đăng xuất.")
    return redirect("home")


@login_required(login_url="login")
def profile(request):
    user = request.user

    if user.is_authenticated:
        if user.is_superuser:
            return render(request, "core/profile.html", {
                "user": user
            })
        id_vaitro = user.vaitro.id_vaitro
        if id_vaitro is not None:
            return render(request, "core/profile.html", {
                "user": user
            })
    return render(request, "core/message.html", {
        "error": "Bạn chưa đăng nhập"
    })

# def register(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password1 = request.POST.get("password1")
#         password2 = request.POST.get("password2")
#         vaitro_string = request.POST.get("vaitro")
#         match vaitro_string:
#             case "admin":
#                 vaitro=get_object_or_404(VaiTro, id_vaitro=1)
#         match vaitro_string:
#             case "user":
#                 vaitro=get_object_or_404(VaiTro, id_vaitro=2)
#         match vaitro_string:
#             case "ketoan":
#                 vaitro=get_object_or_404(VaiTro, id_vaitro=3)

#         # 1. Kiểm tra dữ liệu
#         if not username or not password1 or not password2:
#             return render(request, "core/register.html", {
#                 "error": "Vui lòng nhập đầy đủ thông tin."
#             })

#         if password1 != password2:
#             return render(request, "core/register.html", {
#                 "error": "Mật khẩu không khớp"
#             })

#         if TaiKhoan.objects.filter(username=username).exists():
#             return render(request, "core/register.html", {
#                 "error": "Tên đăng nhập đã tồn tại "
#             })

#         # 2. Tạo tài khoản
#         taikhoan = TaiKhoan.objects.create(
#             username=username,
#             password=make_password(password1),  # 🔐 mã hóa mật khẩu
#             vaitro=vaitro,
#             is_active=True,
#             is_staff=False
#         )

#         # 3. Tự động đăng nhập sau khi đăng ký
#         login(request, taikhoan)

#         messages.success(request, "Đăng ký thành công!")
#         return redirect("home")


def login_view(request):
    if request.method == "POST":
        username_request = request.POST.get("username")
        password_request = request.POST.get("password")

        user = authenticate(request, username=username_request,
                            password=password_request)
        print(username_request+'\n'+password_request)
        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("admin_home")

            id_vaitro = request.user.vaitro.id_vaitro
            if id_vaitro is not None:
                if id_vaitro == 1 or id_vaitro == 2:
                    return redirect("admin_home")
                if id_vaitro == 3:
                    return redirect("accountant_home")
        else:
            return render(request, "core/login.html", {
                "error": "Sai tên đăng nhập hoặc mật khẩu"
            })

    return render(request, "core/login.html")


@login_required(login_url="login")
def admin_home(request):

    HoKhaus = HoKhau.objects.all()
    return render(request, 'core/admin_home.html', {'admin_home': HoKhaus})


@login_required(login_url="login")
def accountant_home(request):

    return render(request, 'core/Accountant.html')

# ========================================================
# 2. CÁC HÀM CHỨC NĂNG KHÁC
# ========================================================


def test(request):
    ds_ho_khau = HoKhau.objects.all()
    return render(request, 'core/test.html', {'ho_khau_list': ds_ho_khau})


@login_required(login_url="login")
def edit_nhan_khau(request, id_nhankhau):
    nk = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)
    if request.method == "POST":
        nk.ho_ten = request.POST.get('ho_ten')
        nk.ngay_sinh = request.POST.get('ngay_sinh') or None
        nk.cccd = request.POST.get('cccd') or None
        nk.quan_he_chu_ho = request.POST.get('quan_he_chu_ho') or None
        ho_khau_id = request.POST.get('ho_khau_id')

        if ho_khau_id:
            nk.id_hokhau_id = ho_khau_id

        nk.save()
        return redirect('nhan_khau_profile', id_nhankhau=nk.id_nhankhau)

    return render(request, 'core/demomanage_edit.html', {'nhan_khau': nk})


@login_required(login_url="login")
def nhan_khau_profile(request, id_nhankhau):
    nhan_khau = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)
    return render(request, 'core/nhan_khau_profile.html', {'nhan_khau': nhan_khau})


@login_required(login_url="login")
def nhan_khau_delete(request, id_nhankhau):
    exists = NhanKhau.objects.filter(id_nhankhau=id_nhankhau).exists()
    if (exists):
        nhan_khau = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)
        nhan_khau.is_deleted = True
        nhan_khau.save()

    return render(request, 'core/demomanage_delete.html')


@login_required(login_url="login")
def export_biendong_excel(request):
    # 1️⃣ Lấy dữ liệu
    biendongs = (
        BienDongNhanKhau.objects
        .select_related('id_nhankhau')
        .order_by('-ngay_batdau')
    )

    # 2️⃣ Tạo workbook & sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Biến động nhân khẩu"

    # 3️⃣ Header
    ws.append([
        "ID Biến động",
        "Họ tên",
        "Loại biến động",
        "Ngày bắt đầu",
        "Ngày kết thúc",
        "Lý do"
    ])

    # 4️⃣ Ghi dữ liệu
    for bd in biendongs:
        ws.append([
            bd.id_biendong,
            bd.id_nhankhau.ho_ten,
            bd.loai_biendong,
            bd.ngay_batdau.strftime('%d/%m/%Y') if bd.ngay_batdau else "",
            bd.ngay_ketthuc.strftime('%d/%m/%Y') if bd.ngay_ketthuc else "",
            bd.ly_do or ""
        ])

    # 5️⃣ Trả file Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="biendong_nhankhau.xlsx"'

    wb.save(response)
    return response


@login_required(login_url="login")
def export_nhankhau_excel(request):
    # 1️⃣ Lấy dữ liệu
    nhankhau = (
        NhanKhau.objects
        .filter(is_deleted=False)
    )

    # 2️⃣ Tạo workbook & sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Danh sách nhân khẩu"

    # 3️⃣ Header
    ws.append([
        "ID Nhân khẩu",
        "Họ tên",
        "Ngày sinh",
        "CCCD",
        "Quan hệ chủ hộ",
        "ID hộ khẩu"
    ])

    # 4️⃣ Ghi dữ liệu
    for nk in nhankhau:
        ws.append([
            nk.id_nhankhau,
            nk.ho_ten,
            nk.ngay_sinh,
            nk.cccd,
            nk.quan_he_chu_ho,
            nk.id_nhankhau
        ])

    # 5️⃣ Trả file Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="danh_sach_nhan_khau.xlsx"'

    wb.save(response)
    return response


@login_required(login_url="login")
def export_hokhau_excel(request):
    # 1️⃣ Lấy dữ liệu
    hokhau = (
        HoKhau.objects.filter(is_deleted=False)
    )

    # 2️⃣ Tạo workbook & sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Biến động nhân khẩu"

    # 3️⃣ Header
    ws.append([
        "ID Hộ Khẩu",
        "Số căn hộ",
        "Diện tích"
    ])

    # 4️⃣ Ghi dữ liệu
    for hk in hokhau:
        ws.append([
            hk.id_hokhau,
            hk.so_can_ho,
            hk.dien_tich
        ])

    # 5️⃣ Trả file Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="danh_sach_ho_khau.xlsx"'

    wb.save(response)
    return response


@login_required(login_url="login")
def add_demo(request):
    if request.method == "POST":
        ho_ten = request.POST.get('ho_ten')
        ngay_sinh = request.POST.get('ngay_sinh')
        cccd = request.POST.get('cccd')
        quan_he_chu_ho = request.POST.get('quan_he_chu_ho')
        ho_khau_id = request.POST.get('ho_khau_id')
        loai_bien_dong_query = request.POST.get('loai_dang_ky_cu_tru')
        try:
            if HoKhau.objects.filter(id_hokhau=ho_khau_id).exists():
                nhan_khau = NhanKhau.objects.create(
                    ho_ten=ho_ten,
                    ngay_sinh=ngay_sinh or None,
                    cccd=cccd or None,
                    quan_he_chu_ho=quan_he_chu_ho or None,
                    id_hokhau_id=int(ho_khau_id)
                )
                BienDongNhanKhau.objects.create(
                    loai_biendong=loai_bien_dong_query,  # hoặc TAM_VANG
                    ngay_batdau=timezone.now().date(),
                    id_nhankhau=nhan_khau,
                    ly_do="Dang ky nhan khau moi"
                )

        except HoKhau.DoesNotExist:
            pass

        return redirect('demomanage/adddemo')

    return render(request, 'core/demomanage_add.html')

# def login(request):
#     # Xử lý khi người dùng NHẤN NÚT (gửi form)
#     if request.method == 'POST':

#         # Xác định xem form Admin hay User được gửi
#         if 'username_admin' in request.POST:
#             user_nhap = request.POST.get('username_admin')
#             pass_nhap = request.POST.get('password_admin')
#             # Đảm bảo tên vai trò này KHỚP CHÍNH XÁC với CSDL của bạn
#             vaitro_mong_muon = 1 # (1 = admin)

#         elif 'username_user' in request.POST:
#             user_nhap = request.POST.get('username_user')
#             pass_nhap = request.POST.get('password_user')
#             # Đảm bảo tên vai trò này KHỚP CHÍNH XÁC với CSDL của bạn
#             vaitro_mong_muon = 3 # (3 = kế toán, hoặc vai trò người dùng)

#         else:
#             user_nhap = None

#         if user_nhap:
#             try:
#                 # Bước 2: Tìm tài khoản trong CSDL
#                 tai_khoan = TaiKhoan.objects.get(username=user_nhap)

#                 # Bước 3: Kiểm tra mật khẩu
#                 if pass_nhap == tai_khoan.password:

#                     # === SỬA LẠI DÒNG NÀY ===
#                     # Bước 4: Kiểm tra vai trò (So sánh SỐ với SỐ)
#                     if tai_khoan.vaitro_id == vaitro_mong_muon:
#                     # === KẾT THÚC SỬA ===

#                         # BƯỚC 5: ĐĂNG NHẬP
#                         # Dùng hàm 'auth_login' chúng ta đã import
#                         request.session['id_taikhoan'] = tai_khoan.id_taikhoan

#                         # Dựa theo thông tin trước đó, 1=Admin, 3=Kế toán

#                         if vaitro_mong_muon == 3: # NẾU LÀ KẾ TOÁN
#                             return redirect('accountant_home') # <-- Đi đến trang Kế toán
#                         else: # NẾU LÀ ADMIN HOẶC VAI TRÒ KHÁC
#                             return redirect('home') # <-- Đi đến trang chủ chung
#                     else:
#                         # Vai trò sai
#                         messages.error(request, "Bạn đang đăng nhập ở form không đúng vai trò!")
#                 else:
#                     # Mật khẩu sai
#                     messages.error(request, "Mật khẩu không đúng!")

#             except TaiKhoan.DoesNotExist:
#                 # Không tìm thấy username
#                 messages.error(request, "Tên đăng nhập không tồn tại!")

#         # Nếu có bất kỳ lỗi nào, render lại trang login
#         # (Template sẽ tự động hiển thị các 'messages' lỗi)
#         return render(request, 'core/login.html')

#     else:
#         # Xử lý khi người dùng MỞ TRANG (yêu cầu GET)
#         # Chỉ cần hiển thị trang login
#         return render(request, 'core/login.html')


@login_required(login_url="login")
def demomanage(request):
    nhan_khau_list = NhanKhau.objects.filter(is_deleted=False)
    query = request.GET.get('search_id', '')
    if query:
        try:
            for a in nhan_khau_list:
                if (a.id_nhankhau == int(query)):
                    nhan_khau_list = [a]
        except ValueError:
            nhan_khau_list = NhanKhau.objects.all()

    data = []
    for nk in nhan_khau_list:
        bien_dong = (
            BienDongNhanKhau.objects
            .filter(id_nhankhau=nk)
            .order_by('-ngay_batdau')
            .first()
        )

        trang_thai = bien_dong.loai_biendong if bien_dong else "Chưa xác định"

        data.append({
            'nhan_khau': nk,
            'trang_thai': trang_thai
        })
    context = {
        'data': data,
        'query': query,
    }
    return render(request, 'core/demomanage.html', context)


@login_required(login_url="login")
def biendong_list(request):
    biendongs = (
        BienDongNhanKhau.objects
        .select_related('id_nhankhau')
        .order_by('-ngay_batdau')
    )

    return render(
        request,
        'core/biendong_list.html',
        {'biendongs': biendongs}
    )


@login_required(login_url="login")
def dang_ky_bdbk(request, id_nhankhau):
    nhan_khau = get_object_or_404(NhanKhau, id_nhankhau=id_nhankhau)

    if request.method == "POST":
        ngay_batdau = request.POST.get('ngay_batdau')
        ngay_ketthuc = request.POST.get('ngay_ketthuc')
        loai_bien_dong = request.POST.get('loai_bien_dong')
        ly_do = request.POST.get('ly_do')

        with transaction.atomic():
            BienDongNhanKhau.objects.create(
                loai_biendong=loai_bien_dong,      # 🔒 cố định
                ngay_batdau=ngay_batdau or timezone.now().date(),
                ngay_ketthuc=ngay_ketthuc or None,
                ly_do=ly_do or None,
                id_nhankhau=nhan_khau
            )

        return redirect('biendong_list')  # hoặc trang chi tiết nhân khẩu

    return render(
        request,
        'core/dangkybdnk.html',
        {'nhan_khau': nhan_khau}
    )


@login_required(login_url="login")
def demomanage_delete(request, id_hokhau):
    exists = HoKhau.objects.filter(id_hokhau=id_hokhau).exists()
    if (exists):
        hr = get_object_or_404(HoKhau, id_hokhau=id_hokhau)
        hr.is_deleted = True
        hr.save()
    return render(request, 'core/hrmanage_delete.html')


@login_required(login_url="login")
def accountmanage(request):
    tai_khoan_list = TaiKhoan.objects.all()
    query = request.GET.get('search_id', '')
    user = request.user
    print(user.is_authenticated)
    if user.is_authenticated:
        id_vaitro = request.user.vaitro.id_vaitro
        if id_vaitro is not None:
            if id_vaitro == 1:
                if query:
                    try:
                        for a in tai_khoan_list:
                            if (a.id_taikhoan == int(query)):
                                tai_khoan_list = [a]
                    except ValueError:
                        tai_khoan_list = TaiKhoan.objects.all()

                context = {
                    'tai_khoan_list': tai_khoan_list,
                    'query': query,
                }

                return render(request, 'core/accountmanage.html', context)
    return render(request, "core/message.html", {
        "error": "Bạn không có quyền truy cập trang này"
    })


@login_required(login_url="login")
def accountmanage_delete(request, id_taikhoan):
    exists = TaiKhoan.objects.filter(id_taikhoan=id_taikhoan).exists()
    if (exists):
        account = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)
        account.is_deleted = True
    return render(request, 'core/accountmanage_delete.html')


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

        # 1. Kiểm tra dữ liệu
        if not username or not password1 or not password2:
            return render(request, "core/accountmanage_addaccount.html", {
                "error": "Vui lòng nhập đầy đủ thông tin."
            })

        if password1 != password2:
            return render(request, "core/accountmanage_addaccount.html", {
                "error": "Mật khẩu không khớp"
            })

        if TaiKhoan.objects.filter(username=username).exists():
            return render(request, "core/accountmanage_addaccount.html", {
                "error": "Tên đăng nhập đã tồn tại "
            })

        # 2. Tạo tài khoản
        taikhoan = TaiKhoan.objects.create(
            username=username,
            password=make_password(password1),  # 🔐 mã hóa mật khẩu
            vaitro=vaitro,
            is_active=True,
            is_staff=False
        )

    return render(request, 'core/accountmanage_addaccount.html', {
        "error": "Tạo tài khoản thành công "
    })


@login_required(login_url="login")
def view_taikhoan(request, id_taikhoan):

    user = authenticate(request, username="admin", password="2005")
    login(request, user)

    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)
    return render(request, 'core/accountmanage_view.html', {'taikhoan': taikhoan})


@login_required(login_url="login")
def edit_taikhoan(request, id_taikhoan):
    taikhoan = get_object_or_404(TaiKhoan, id_taikhoan=id_taikhoan)

    if request.method == "POST":
        username = request.POST.get('username')
        password_raw = request.POST.get('password')
        vaitro_id = request.POST.get('vaitro_id')
        try:
            vaitro = VaiTro.objects.get(id_vaitro=vaitro_id)
            taikhoan.vaitro = vaitro
        except VaiTro.DoesNotExist:
            return render(request, "core/message.html", {
                "error": "ID vai trò không tồn tại"
            })
        if not taikhoan.username == username:
            if not TaiKhoan.objects.filter(username=username).exists():
                taikhoan.username = username
            else:
                return render(request, "core/message.html", {
                    "error": "username này đã tồn tại"
                })

        taikhoan.set_password(password_raw)

        taikhoan.save()
        return render(request, "core/message.html", {
            "error": "Thay đổi thông tin thành công"
        })
    return render(request, 'core/accountmanage_change.html', {'taikhoan': taikhoan})


@login_required(login_url="login")
def hrmanage(request):
    print(2)
    ds_ho_khau = HoKhau.objects.all()
    query = request.GET.get('search_id', '')
    if query:
        try:
            for a in ds_ho_khau:
                if (a.id_hokhau == int(query)):
                    ds_ho_khau = [a]
        except ValueError:
            ds_ho_khau = HoKhau.objects.all()

    context = {
        'ho_khau_list': ds_ho_khau,
        'query': query,
    }

    return render(request, 'core/hrmanage.html', context)


@login_required(login_url="login")
def hrmanage_delete(request, id_hokhau):
    exists = HoKhau.objects.filter(id_hokhau=id_hokhau).exists()
    if (exists):
        hr = get_object_or_404(HoKhau, id_hokhau=id_hokhau)
        hr.is_deleted = True
    return render(request, 'core/hrmanage_delete.html')


@login_required(login_url="login")
def add_hokhau(request):
    if request.method == "POST":
        so_can_ho = request.POST.get('so_can_ho')
        dien_tich = request.POST.get('dien_tich')

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

        return redirect('add_hokhau')

    return render(request, 'core/add_hokhau.html')


@login_required(login_url="login")
def hokhau_detail(request, id_hokhau):
    print(3)
    hokhau = HoKhau.objects.get(id_hokhau=id_hokhau)
    print(hokhau.id_hokhau)
    thanh_vien = NhanKhau.objects.filter(
        id_hokhau_id=id_hokhau, is_deleted=False)

    return render(request, 'core/hokhau_detail.html', {
        'hokhau': hokhau,
        'thanh_vien': thanh_vien
    })


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
                return redirect('hrmanage')
            except ValueError:
                messages.error(request, "Diện tích phải là số hợp lệ!")

    return render(request, 'core/hokhau_edit.html', {'hokhau': hokhau})


@login_required(login_url="login")
def HoKhaus_list(request):
    HoKhaus = HoKhau.objects.all()
    return render(request, 'core/HoKhaus_list.html', {'HoKhaus': HoKhaus})


# ============= Kế toán Views =================
@login_required(login_url="login")
def accountant_home(request):
    return render(request, 'core/Accountant.html')


@login_required(login_url="login")
# Quan lý khoản thu
def fee_management(request):
    query = request.GET.get('search_khoanthu')  # Lấy tham số tìm kiếm từ URL
    khoan_thu_list = KhoanThu.objects.all()  # Lấy dữ liệu từ database

    if query:
        khoan_thu_list = khoan_thu_list.filter(
            Q(ten_khoanthu__icontains=query) | Q(id_khoanthu__icontains=query)
        )
    total_count = khoan_thu_list.count()
    form = KhoanThuForm()
    context = {
        'khoan_thu_list': khoan_thu_list,
        'total_count': total_count,
        'form': form,
        'query': query
    }
    return render(request, 'core/FeeManagement.html', context)


@login_required(login_url="login")
def view_khoanthu_detail_modal(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        pass
    return render(request, 'core/ViewFeeDetailModal.html', {'khoan_thu': khoan_thu})


@login_required(login_url="login")
def add_khoanthu(request):
    if request.method == 'POST':
        form = KhoanThuForm(request.POST)
        if form.is_valid():
            new_ID = form.cleaned_data.get('id_khoanthu')
            # Kiểm tra trùng mã khoản thu
            if KhoanThu.objects.filter(id_khoanthu=new_ID).exists():
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Mã khoản thu này đã tồn tại!'}, status=400)
                messages.error(request, 'Mã khoản thu này đã tồn tại!')
                return render(request, 'core/AddFeeModal.html', {'form': form})

            form.save()
            # Nếu là yêu cầu từ Modal (AJAX)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            # Nếu là yêu cầu thông thường, quay lại trang quản lý khoản thu
            messages.success(request, 'Thêm khoản thu thành công!')
            return redirect('fee_management')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Dữ liệu không hợp lệ!'}, status=400)
    else:
        form = KhoanThuForm()
    return render(request, 'core/AddFeeModal.html', {'form': form})


@login_required(login_url="login")
def edit_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)

    if request.method == 'POST':
        form = KhoanThuForm(request.POST, instance=khoan_thu)

        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            messages.success(
                request, f"Khoản thu '{khoan_thu.ten_khoanthu}' đã được cập nhật thành công!")
            return redirect('fee_management')
        else:
            context = {'form': form, 'khoan_thu': khoan_thu}
            return render(request, 'core/EditFeeModal.html', context, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = KhoanThuForm(instance=khoan_thu)
        context = {'form': form, 'khoan_thu': khoan_thu}
        return render(request, 'core/EditFeeModal.html', context)
    else:
        form = KhoanThuForm(instance=khoan_thu)
        context = {
            'form': form,
            'khoan_thu': khoan_thu,
            'page_title': f"CHỈNH SỬA KHOẢN THU - {khoan_thu.ten_khoanthu}",
        }
        return render(request, 'core/EditFee.html', context)


@login_required(login_url="login")
def delete_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, id_khoanthu=pk)

    if request.method == 'POST':
        khoan_thu.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Khoản thu đã được xóa thành công!'})
        return redirect('fee_management')
    return render(request, 'core/DeleteFeeModal.html', {'khoan_thu': khoan_thu})


@login_required(login_url="login")
# Quản lý đợt thu phí
def fee_collection_period(request):
    query = request.GET.get('search_dotthu')
    dot_thu_phi_list = DotThuPhi.objects.select_related('id_khoanthu').all()
    active_count = dot_thu_phi_list.filter(trang_thai='open').count()
    if query:
        dot_thu_phi_list = dot_thu_phi_list.filter(
            Q(ten_dotthu__icontains=query) | Q(id_dotthu__icontains=query)
        )
    context = {
        'dot_thu_phi_list': dot_thu_phi_list,
        'active_count': active_count,
        'query': query
    }
    return render(request, 'core/FeeCollectionPeriod.html', context)


@login_required(login_url="login")
def view_dotthu_detail_modal(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    danh_sach_hoa_don = dot_thu.hoa_dons.select_related(
        'id_hokhau').all().order_by('id_hokhau__so_can_ho')
    ids_da_co = danh_sach_hoa_don.values_list('id_hokhau_id', flat=True)
    tat_ca_ho_khau = HoKhau.objects.exclude(id_hokhau__in=ids_da_co)
    context = {
        'dot_thu': dot_thu,
        'danh_sach_hoa_don': danh_sach_hoa_don,
        'tat_ca_ho_khau': tat_ca_ho_khau  # Biến này dùng để hiển thị trong phần "Thêm hộ"
    }
    return render(request, 'core/ViewPeriodDetailModal.html', context)


@login_required(login_url="login")
def update_payment_status(request):
    invoice_ids = request.POST.getlist(
        'invoice_ids[]')  # Nhận danh sách ID từ AJAX

    if not invoice_ids:
        return JsonResponse({'status': 'error', 'message': 'Không có hóa đơn nào được chọn'}, status=400)

    try:
        # Cập nhật ngày nộp là ngày hiện tại cho các hóa đơn được chọn
        HoaDon.objects.filter(id_hoadon__in=invoice_ids, ngay_nop__isnull=True).update(
            ngay_nop=timezone.now()
        )
        return JsonResponse({'status': 'success', 'message': 'Cập nhật trạng thái thành công'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required(login_url="login")
def create_invoices_for_period(request):
    id_dotthu = request.POST.get('id_dotthu')
    hokhau_ids = request.POST.getlist('hokhau_ids[]')
    multipliers = request.POST.getlist('multipliers[]')
    prices = request.POST.getlist('prices[]')

    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=id_dotthu)
    last_invoice = HoaDon.objects.all().order_by('id_hoadon').last()
    next_id = (last_invoice.id_hoadon + 1) if last_invoice else 1

    for hk_id, mult, price in zip(hokhau_ids, multipliers, prices):
        hokhau = get_object_or_404(HoKhau, id_hokhau=hk_id)

        if not HoaDon.objects.filter(id_dotthu=dot_thu, id_hokhau=hokhau).exists():
            # Tính toán: Tổng tiền = Đơn giá x Hệ số
            final_amount = float(price) * float(mult)

            HoaDon.objects.create(
                id_hoadon=next_id,
                id_dotthu=dot_thu,
                id_hokhau=hokhau,
                tong_tien=final_amount
            )
            next_id += 1
    danh_sach_hoa_don = dot_thu.hoa_dons.select_related(
        'id_hokhau').all().order_by('id_hokhau__so_can_ho')
    tat_ca_ho_khau = HoKhau.objects.exclude(
        id_hokhau__in=danh_sach_hoa_don.values_list('id_hokhau_id', flat=True))

    return render(request, 'core/ViewPeriodDetailModal.html', {
        'dot_thu': dot_thu,
        'danh_sach_hoa_don': danh_sach_hoa_don,
        'tat_ca_ho_khau': tat_ca_ho_khau
    })


@login_required(login_url="login")
def add_dotthu(request):
    if request.method == 'POST':
        form = DotThuPhiForm(request.POST)
        if form.is_valid():
            new_ID = form.cleaned_data.get('id_dotthu')
            if DotThuPhi.objects.filter(id_dotthu=new_ID).exists():
                return JsonResponse({'error': 'Mã đợt thu phí này đã tồn tại!'}, status=400)

            form.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            return redirect('fee_collection_period')
    else:
        form = DotThuPhiForm()
    return render(request, 'core/AddPeriodModal.html', {'form': form})


@login_required(login_url="login")
def edit_dotthu(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    if request.method == 'POST':
        form = DotThuPhiForm(request.POST, instance=dot_thu)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('fee_collection_period')
        else:
            return render(request, 'core/EditPeriodModal.html', {'form': form, 'dot_thu': dot_thu}, status=400)

    form = DotThuPhiForm(instance=dot_thu)
    return render(request, 'core/EditPeriodModal.html', {'form': form, 'dot_thu': dot_thu})


@login_required(login_url="login")
def delete_dotthu(request, pk):
    dot_thu = get_object_or_404(DotThuPhi, id_dotthu=pk)
    if request.method == 'POST':
        dot_thu.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Đợt thu phí đã được xóa thành công!'})
        return redirect('fee_collection_period')
    return render(request, 'core/DeletePeriodModal.html', {'dot_thu': dot_thu})

# Thống kê


@login_required(login_url="login")
def statistics_view(request):
    # Lấy năm từ tham số GET, mặc định là năm hiện tại
    year_str = request.GET.get('year', str(datetime.now().year))
    try:
        year = int(year_str)
    except ValueError:
        year = datetime.now().year

    # 1. Biểu đồ tròn: Cơ cấu loại khoản thu theo doanh thu trong NĂM ĐÃ CHỌN
    phi_status = KhoanThu.objects.filter(
        dot_thuphi__hoa_dons__ngay_nop__year=year
    ).annotate(
        total_revenue=Sum('dot_thuphi__hoa_dons__tong_tien')
    ).order_by('-total_revenue')[:5]

    pie_labels = [item.ten_khoanthu for item in phi_status]
    pie_data = [float(item.total_revenue) for item in phi_status]

    # 2. Biểu đồ đường: Xu hướng doanh thu theo tháng
    monthly_income = HoaDon.objects.filter(ngay_nop__year=year).annotate(
        month=ExtractMonth('ngay_nop')
    ).values('month').annotate(total=Sum('tong_tien')).order_by('month')

    line_labels = ["T1", "T2", "T3", "T4", "T5",
                   "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
    line_data = [0] * 12
    for item in monthly_income:
        if item['month']:
            line_data[item['month'] - 1] = float(item['total'])

    # 3. Tính toán các con số tổng quan
    tong_da_thu = HoaDon.objects.filter(ngay_nop__year=year).aggregate(
        Sum('tong_tien'))['tong_tien__sum'] or 0

    so_ho = HoKhau.objects.filter(is_active=True).count()
    dot_thus = DotThuPhi.objects.filter(ngay_batdau__year=year)
    tong_can_thu = 0
    for dot in dot_thus:
        # Mục tiêu dự kiến = Đơn giá x Số hộ (Đơn giản hóa)
        tong_can_thu += float(dot.id_khoanthu.don_gia) * so_ho

    phan_tram = round((float(tong_da_thu) / tong_can_thu)
                      * 100, 1) if tong_can_thu > 0 else 0

    context = {
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'line_labels': json.dumps(line_labels),
        'line_data': json.dumps(line_data),
        'tong_da_thu': tong_da_thu,
        'tong_can_thu': tong_can_thu,
        'phan_tram': phan_tram,
        'selected_year': year,
    }
    return render(request, 'core/Statistics.html', context)


@login_required(login_url="login")
def export_finance_excel(request):
    year_str = request.GET.get('year', str(timezone.now().year))
    try:
        year = int(year_str)
    except ValueError:
        year = timezone.now().year

    wb = Workbook()
    ws = wb.active
    ws.title = f"Thong ke {year}"

    # Định dạng
    bold_font = Font(bold=True, color="FFFFFF")
    center_align = Alignment(horizontal='center', vertical='center')
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    header_fill = PatternFill(start_color="1976D2",
                              end_color="1976D2", fill_type="solid")

    # Tiêu đề báo cáo
    ws.merge_cells('A1:C1')
    ws['A1'] = f"BÁO CÁO TÀI CHÍNH NĂM {year} - CHUNG CƯ BLUEMOON"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = center_align

    # Header bảng
    headers = ['Tháng', 'Số lượng hóa đơn', 'Doanh thu thực tế (VND)']
    ws.append([])  # Dòng trống
    ws.append(headers)

    # Định dạng dòng Header (Dòng số 3)
    for cell in ws[3]:
        cell.font = bold_font
        cell.fill = header_fill  # Sử dụng biến header_fill đã tạo
        cell.alignment = center_align
        cell.border = border

    # Lấy dữ liệu và điền vào bảng
    monthly_data = HoaDon.objects.filter(ngay_nop__year=year).annotate(
        month=ExtractMonth('ngay_nop')
    ).values('month').annotate(
        count=Count('id_hoadon'),
        total=Sum('tong_tien')
    ).order_by('month')

    total_year_money = 0
    for m in range(1, 13):
        data = next(
            (item for item in monthly_data if item['month'] == m), None)
        count = data['count'] if data else 0
        money = float(data['total']) if data else 0
        total_year_money += money

        ws.append([f"Tháng {m}", count, money])
        for cell in ws[ws.max_row]:
            cell.border = border
            cell.alignment = Alignment(horizontal='right') if isinstance(
                cell.value, (int, float)) else center_align

    # Dòng tổng cộng
    ws.append(["TỔNG CỘNG", "", total_year_money])
    last_row = ws.max_row
    ws.cell(row=last_row, column=1).font = Font(bold=True)
    ws.cell(row=last_row, column=3).font = Font(bold=True)
    for cell in ws[last_row]:
        cell.border = border

    # Chỉnh độ rộng cột
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 25

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=BaoCao_BlueMoon_{year}.xlsx'
    wb.save(response)
    return response


@login_required(login_url="login")
def invoice_history(request):
    query = request.GET.get('search_invoice', '')
    selected_month = request.GET.get('month', '')
    selected_year = request.GET.get('year', '')
    invoice_list = HoaDon.objects.select_related(
        'id_hokhau', 'id_dotthu').all().order_by('-ngay_nop')
    if query:
        invoice_list = invoice_list.filter(
            Q(id_hoadon__icontains=query) |
            Q(id_hokhau__so_can_ho__icontains=query)
        )

    if selected_month:
        invoice_list = invoice_list.annotate(
            month=ExtractMonth('ngay_nop')).filter(month=selected_month)
    if selected_year:
        invoice_list = invoice_list.annotate(
            year=ExtractYear('ngay_nop')).filter(year=selected_year)
    context = {
        'invoice_list': invoice_list,
        'query': query,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'years': range(2020, datetime.now().year+1),
        'months': range(1, 13),

    }
    return render(request, 'core/InvoiceHistory.html', context)


@login_required(login_url="login")
def view_invoice_detail_modal(request, pk):
    hoadon = get_object_or_404(
        HoaDon.objects.select_related('id_hokhau', 'id_dotthu__id_khoanthu'),
        id_hoadon=pk)
    return render(request, 'core/ViewInvoiceDetailModal.html', {'hoadon': hoadon})


@login_required(login_url="login")
def delete_invoice_modal(request, pk):
    hoadon = get_object_or_404(HoaDon, id_hoadon=pk)

    if request.method == 'POST':
        if hoadon.ngay_nop is None:
            hoadon.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'Hóa đơn #{pk} đã được xóa thành công!'
                })
            return redirect('invoice_history')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Không thể xóa hóa đơn đã thanh toán!'
                }, status=400)
            return redirect('invoice_history')
    return render(request, 'core/DeleteInvoiceModal.html', {'hoadon': hoadon})
