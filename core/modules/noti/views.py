from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from core.forms import ThongBaoForm
from .models import ThongBao
from django.contrib.auth import get_user_model
from django.db.models import Q
from core.decorators import role_required

# View để BQL gửi thông báo


@login_required(login_url="login")
@role_required([1, 2])
def thongbao_create(request):
    if request.method == "POST":
        form = ThongBaoForm(request.POST)
        if form.is_valid():
            thongbao = form.save(commit=False)
            thongbao.sender = request.user
            thongbao.updated_by = request.user
            thongbao.save()
            messages.success(request, "Đã gửi thông báo!")
            return redirect("thongbao_list")
        else:
            messages.error(request, "Vui lòng nhập đủ thông tin!")
    else:
        form = ThongBaoForm()
    return render(request, "noti/thongbao_form.html", {"form": form})



@login_required(login_url="login")
def thongbao_list(request):
    user = request.user
    vaitro = getattr(
        getattr(request.user, 'vaitro', None), 'id_vaitro', None)
    query = request.GET.get('query', '').strip()
    send_time = request.GET.get('send_time', '').strip()
    if vaitro == 1 or user.is_superuser:  # BQL
        qs = ThongBao.objects.all()
    elif vaitro == 3:  # Kế toán
        qs = ThongBao.objects.filter(
            Q(doi_tuong="all") | Q(doi_tuong="ketoan"))
    elif vaitro == 2:  # Cư dân
        qs = ThongBao.objects.filter(Q(doi_tuong="all") | Q(doi_tuong="cudan"))
    else:
        qs = ThongBao.objects.none()

    qs = qs.filter(is_deleted=False)
    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(sender__username__icontains=query)
        )
    if send_time:
        qs = qs.filter(created_at__date=send_time)
    qs = qs.order_by("-created_at")
    return render(request, "noti/thongbao_list.html", {"thongbao_list": qs, "query": query, "send_time": send_time})


@login_required(login_url="login")
def thongbao_detail(request, pk):
    thongbao = get_object_or_404(ThongBao, pk=pk)
    user = request.user
    vaitro = getattr(
        getattr(request.user, 'vaitro', None), 'id_vaitro', None)
    # BQL xem tất cả
    if vaitro == 1 or user.is_superuser:
        return render(request, "noti/thongbao_detail.html", {"thongbao": thongbao})
    # Kế toán chỉ xem được all hoặc ketoan
    if vaitro == 3 and thongbao.doi_tuong in ["all", "ketoan"]:
        return render(request, "noti/thongbao_detail.html", {"thongbao": thongbao})
    # Cư dân chỉ xem được all hoặc cudan
    if vaitro == 2 and thongbao.doi_tuong in ["all", "cudan"]:
        return render(request, "noti/thongbao_detail.html", {"thongbao": thongbao})
    messages.error(request, "Bạn không có quyền xem thông báo này!")
    return redirect("thongbao_list")


@login_required(login_url="login")
@role_required([1, 2])
def thongbao_delete(request, pk):
    thongbao = get_object_or_404(ThongBao, pk=pk)
    user = request.user
    vaitro = getattr(
        getattr(request.user, 'vaitro', None), 'id_vaitro', None)
    sender_vaitro = getattr(
        getattr(thongbao.sender, 'taikhoan', None), 'vaitro', None)
    
    if not user.is_superuser and vaitro != sender_vaitro:
        messages.error(request, "Bạn không có quyền xóa thông báo này!")
        return redirect("thongbao_list")
    if request.method == "POST":
        thongbao.is_deleted = True
        thongbao.updated_by = request.user.username
        thongbao.save()
        messages.success(request, "Đã xóa thông báo!")
        return redirect("thongbao_list")
    return render(request, "noti/thongbao_confirm_delete.html", {"thongbao": thongbao})


@login_required(login_url="login")
@role_required([1, 2])
def thongbao_update(request, pk):
    thongbao = get_object_or_404(ThongBao, pk=pk)
    user = request.user
    vaitro = getattr(
        getattr(request.user, 'vaitro', None), 'id_vaitro', None)
    sender_vaitro = getattr(
        getattr(thongbao.sender, 'taikhoan', None), 'vaitro', None)
    
    if not user.is_superuser and vaitro != sender_vaitro:
        messages.error(request, "Bạn không có quyền sửa thông báo này!")
        return redirect("thongbao_list")
    
    if request.method == "POST":
        form = ThongBaoForm(request.POST, instance=thongbao)
        if form.is_valid():
            thongbao = form.save(commit=False)
            thongbao.updated_by = request.user.username
            thongbao.save()
            messages.success(request, "Đã cập nhật thông báo!")
            return redirect("thongbao_list")
        else:
            messages.error(request, "Vui lòng nhập đủ thông tin!")
    else:
        form = ThongBaoForm(instance=thongbao)
    return render(request, "noti/thongbao_form.html", {"thongbao": thongbao, "form": form})
