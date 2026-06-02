from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from core.forms import ThongBaoForm, TicketForm, TicketAssignForm, TicketStatusForm, TicketResponseForm
from core.modules.account.models import TaiKhoan
from .models import ThongBao, Ticket, TicketResponse
from core.modules.resident.models import HoKhau
from core.modules.apartment.models import CanHo
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
    sender_vaitro = getattr(thongbao.sender, 'vaitro_id', None)

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


@login_required(login_url="login")
@role_required([1, 2])
def ticket_list(request):
    user = request.user
    vaitro = getattr(user, 'vaitro', None)
    # Query param: chỉ 1 ô search
    query = request.GET.get('search', '').strip()
    created_at = request.GET.get('created_at', '').strip()
    rating = request.GET.get('rating', '').strip()
    status = request.GET.get('status', '').strip()

    if vaitro and vaitro.id_vaitro == 2:
        tickets = Ticket.objects.filter(creator=user, is_deleted=False)
    else:
        tickets = Ticket.objects.filter(is_deleted=False)

    if query:
        tickets = tickets.filter(
            Q(creator__username__icontains=query) |
            Q(creator__chu_ho__id_canho__so_can_ho__icontains=query)
        )
    # Filter by created_at (YYYY-MM-DD)
    if created_at:
        tickets = tickets.filter(created_at__date=created_at)
    # Filter by rating
    if rating:
        tickets = tickets.filter(rating=rating)
    # Filter by status
    if status:
        tickets = tickets.filter(status=status)

    status_choices = Ticket._meta.get_field('status').choices

    context = {
        "tickets": tickets,
        "status_choices": status_choices,
        "search": query,
        "created_at": created_at,
        "rating": rating,
        "status": status,
    }
    return render(request, "ticket/ticket_list.html", context)


@login_required(login_url="login")
@role_required([2])
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creator = request.user
            ticket.save()
            messages.success(request, "Tạo ticket thành công!")
            return redirect("ticket_list")
    else:
        form = TicketForm(user=request.user)
    return render(request, "ticket/ticket_form.html", {"form": form})


@login_required(login_url="login")
@role_required([1])
def ticket_assign(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketAssignForm(
            request.POST, instance=ticket, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.updated_by = str(request.user)
            ticket.save()
            return JsonResponse({"success": True, "assignee_id": ticket.assignee_id})
        else:
            error_msg = form.errors.as_text() or "Dữ liệu không hợp lệ."
            return JsonResponse({"success": False, "error": error_msg}, status=400)
    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ."}, status=405)


@login_required(login_url="login")
@role_required([1])
def ticket_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketStatusForm(
            request.POST, instance=ticket, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.updated_by = str(request.user)
            ticket.save()
            return JsonResponse({"success": True, "status": ticket.status})
        else:
            error_msg = form.errors.as_text() or "Dữ liệu không hợp lệ."
            return JsonResponse({"success": False, "error": error_msg}, status=400)
    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ."}, status=405)


@login_required(login_url="login")
@role_required([1, 2])
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    vaitro = getattr(user, 'vaitro', None)
    # Cư dân chỉ được xem ticket mình tạo
    if vaitro and vaitro.id_vaitro == 2 and ticket.creator != user:
        messages.error(request, "Bạn không có quyền xem ticket này!")
        return redirect("ticket_list")

    responses = ticket.responses.all().order_by("created_at")

    # Role-based permissions and choices
    can_assign = False
    can_change_status = False
    can_review = False
    assignee_choices = []
    status_choices = ticket._meta.get_field('status').choices

    if user.is_superuser or (vaitro and vaitro.id_vaitro == 1):
        can_assign = True
        can_change_status = True
        assignee_choices = TaiKhoan.objects.filter(vaitro__id_vaitro=1)

    # Creator (or superuser) can review when ticket is done.
    if user.is_superuser or ticket.creator == user:
        can_review = True

    return render(request, "ticket/ticket_detail.html", {
        "ticket": ticket,
        "responses": responses,
        "can_assign": can_assign,
        "can_change_status": can_change_status,
        "can_review": can_review,
        "assignee_choices": assignee_choices,
        "status_choices": status_choices,
    })


@login_required(login_url="login")
@role_required([1, 2])
def ticket_review(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    # Only the creator can review their own ticket
    if ticket.creator != user and not user.is_superuser:
        return JsonResponse({"success": False, "error": "Bạn không có quyền đánh giá ticket này."}, status=403)
    if ticket.status != "done":
        return JsonResponse({"success": False, "error": "Chỉ được đánh giá khi ticket đã hoàn thành."}, status=400)
    if ticket.rating is not None:
        return JsonResponse({"success": False, "error": "Ticket này đã được đánh giá."}, status=400)
    if request.method == "POST":
        rating = request.POST.get("rating")
        review = request.POST.get("review", "").strip()
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            ticket.rating = int(rating)
            ticket.review = review
            ticket.updated_by = str(user)
            ticket.save()
            return JsonResponse({"success": True, "rating": ticket.rating, "review": ticket.review})
        return JsonResponse({"success": False, "error": "Điểm không hợp lệ (1-5)."}, status=400)
    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ."}, status=405)


@login_required(login_url="login")
@role_required([1, 2])
def ticket_response(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.responder = request.user
            response.save()
            messages.success(request, "Đã gửi phản hồi!")
            return redirect("ticket_detail", pk=pk)
    else:
        form = TicketResponseForm()
    return render(request, "noti/ticket_response_form.html", {"form": form, "ticket": ticket})


@login_required(login_url="login")
@role_required([1, 2])
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, is_deleted=False)
    user = request.user
    vaitro = getattr(user, 'vaitro', None)

    can_delete = user.is_superuser or ticket.creator == user

    if not can_delete:
        messages.error(request, "Bạn không có quyền xóa ticket này!")
        return redirect("ticket_detail", pk=pk)

    if request.method == "POST":
        ticket.is_deleted = True
        ticket.updated_by = user.username
        ticket.save()
        messages.success(request, "Đã xóa ticket!")
        return redirect("ticket_list")

    return render(request, "ticket/ticket_confirm_delete.html", {"ticket": ticket})
