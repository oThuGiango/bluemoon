from core.forms import CanHoForm, GuiXeForm
from django.db import models
from django.contrib import messages
from core.decorators import role_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import CanHo, Building
from core.modules.resident.models import GuiXe, HoKhau


@login_required(login_url="login")
@role_required([1])
def building_list(request):
    buildings = Building.objects.filter(
        is_active=True, is_deleted=False).order_by("-id")
    return render(request, "apartment/building_list.html", {"buildings": buildings})


@login_required(login_url="login")
@role_required([1])
def building_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        max_floor = request.POST.get("max_floor")
        if name and max_floor:
            try:
                max_floor = int(max_floor)
                Building.objects.create(
                    name=name, max_floor=max_floor, updated_by=request.user.username)
                messages.success(request, f"Đã thêm tòa nhà {name}!")
                return redirect("building_list")
            except ValueError:
                messages.error(request, "Số tầng tối đa phải là số nguyên!")
        else:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin!")
    return render(request, "apartment/building_add.html")


@login_required(login_url="login")
@role_required([1])
def building_edit(request, id):
    building = get_object_or_404(Building, id=id)
    if request.method == "POST":
        name = request.POST.get("name")
        max_floor = request.POST.get("max_floor")
        if name and max_floor:
            try:
                building.name = name
                building.max_floor = int(max_floor)
                building.updated_by = request.user.username
                building.save()
                messages.success(request, "Cập nhật tòa nhà thành công!")
                return redirect("building_list")
            except ValueError:
                messages.error(request, "Số tầng tối đa phải là số nguyên!")
        else:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin!")
    return render(request, "apartment/building_edit.html", {"building": building})


@login_required(login_url="login")
@role_required([1])
def building_delete(request, id):
    building = get_object_or_404(Building, id=id)
    if request.method == "POST":
        building.is_active = False
        building.save()
        messages.success(request, f"Đã xóa tòa nhà {building.name}!")
        return redirect("building_list")
    return render(request, "apartment/building_delete.html", {"building": building})


@login_required(login_url="login")
@role_required([1])
def building_detail(request, id):
    building = get_object_or_404(Building, id=id)
    return render(request, "apartment/building_detail.html", {"building": building})


@login_required(login_url="login")
@role_required([1])
def canho_list(request):

    building_list = Building.objects.filter(is_active=True, is_deleted=False)
    query = request.GET.get("search_canho", "")
    status = request.GET.get('status')
    apartment_type = request.GET.get('type')
    building = request.GET.get('building')
    floor = request.GET.get('floor')

    canho_list = CanHo.objects.filter(is_deleted=False).order_by("-id_canho")
    if apartment_type:
        canho_list = canho_list.filter(apartment_type=apartment_type)
    if status:
        canho_list = canho_list.filter(status=status)
    if building:
        canho_list = canho_list.filter(building_id=building)
    if floor:
        canho_list = canho_list.filter(floor=floor)
    if query:
        canho_list = canho_list.filter(so_can_ho__icontains=query)

    max_floor = Building.objects.filter(is_active=True, is_deleted=False).aggregate(
        models.Max('max_floor'))['max_floor__max']
    if building:
        try:
            selected_building = Building.objects.get(id=building)
            max_floor = selected_building.max_floor
        except Building.DoesNotExist:
            pass

    total_count = canho_list.count()
    context = {
        "canho_list": canho_list,
        "query": query,
        "status": status,
        "type": apartment_type,
        "building_list": building_list,
        "building": building,
        "floor": floor,
        "max_floor": list(range(1, max_floor + 1)) if max_floor else [],
        "total_count": total_count,
    }
    return render(request, "apartment/canho.html", context)


@login_required(login_url="login")
@role_required([1])
def canho_add(request):
    if request.method == "POST":
        form = CanHoForm(request.POST)
        if form.is_valid():
            canho = form.save(commit=False)
            canho.updated_by = request.user.username
            canho.save()
            messages.success(
                request, f"Căn hộ {form.cleaned_data.get('so_can_ho')} đã được thêm thành công!")
            return redirect("canho_list")
        else:
            messages.error(request, "Vui lòng kiểm tra lại các trường!")
    else:
        form = CanHoForm()
    return render(request, "apartment/canho_add.html", {"form": form})


@login_required(login_url="login")
@role_required([1])
def canho_edit(request, id_canho):
    canho = get_object_or_404(CanHo, id_canho=id_canho)
    if request.method == "POST":
        form = CanHoForm(request.POST, instance=canho)
        if form.is_valid():
            canho = form.save(commit=False)
            canho.updated_by = request.user.username
            canho.save()
            messages.success(request, "Cập nhật thông tin căn hộ thành công!")
            return redirect("canho_list")
        else:
            # Lấy tất cả lỗi của form (bao gồm cả lỗi trường và lỗi chung)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label if field in form.fields else field}: {error}")
            # Nếu có lỗi chung (non_field_errors)
            for error in form.non_field_errors():
                messages.error(request, error)
            return redirect('canho_list')
    else:
        form = CanHoForm(instance=canho)
    return render(request, "apartment/canho_edit.html", {"form": form, "canho": canho})


@login_required(login_url="login")
@role_required([1])
def canho_delete(request, id_canho):
    canho = get_object_or_404(CanHo, id_canho=id_canho)
    if request.method == "POST":
        canho.is_deleted = True
        canho.save()
        messages.success(request, f"Căn hộ {canho.so_can_ho} đã được xóa!")
        return redirect("canho_list")
    return render(request, "core/canho_delete.html", {"canho": canho})


@login_required(login_url="login")
@role_required([1])
def canho_detail(request, id_canho):
    canho = get_object_or_404(CanHo, id_canho=id_canho)
    hokhau_list = HoKhau.objects.filter(id_canho=canho, is_deleted=False)
    return render(request, "core/canho_detail.html", {"canho": canho, "hokhau_list": hokhau_list})


def get_hokhau_for_user(request):
    # vaitro=2: chỉ xem được xe của hộ khẩu mình làm chủ hộ
    if hasattr(request.user, 'taikhoan') and getattr(request.user.taikhoan, 'vaitro', None) == 2:
        return HoKhau.objects.filter(id_chuho=request.user.taikhoan, is_deleted=False, is_active=True)
    return HoKhau.objects.filter(is_deleted=False, is_active=True)


@login_required(login_url="login")
@role_required([1, 2])
def guixe_list(request):
    query = request.GET.get('query', '').strip()
    type = request.GET.get('type', '')
    # Nếu vaitro=2 thì chỉ lấy xe của các hộ khẩu mà user là chủ hộ
    if hasattr(request.user, 'taikhoan') and getattr(request.user.taikhoan, 'vaitro', None) == 2:
        hokhau_qs = get_hokhau_for_user(request)
        guixe_qs = GuiXe.objects.filter(hokhau__in=hokhau_qs, is_deleted=False)
    else:
        guixe_qs = GuiXe.objects.filter(is_deleted=False)

    if type:
        guixe_qs = guixe_qs.filter(loai_xe=type)
    if query:
        guixe_qs = guixe_qs.filter(
            models.Q(bien_so__icontains=query) |
            models.Q(hokhau__id_canho__so_can_ho__icontains=query)
        )

    context = {'guixe_list': guixe_qs, 'type': type, 'query': query}
    return render(request, 'apartment/guixe/list.html', context)


@login_required(login_url="login")
@role_required([1, 2])
def guixe_add(request):
    hokhau_qs = get_hokhau_for_user(request)
    if request.method == 'POST':
        form = GuiXeForm(request.POST, hokhau_qs=hokhau_qs,
                         disabled_hokhau=False)
        if form.is_valid():
            guixe = form.save(commit=False)
            guixe.hokhau = form.cleaned_data['hokhau']
            guixe.updated_by = request.user.username
            guixe.save()
            messages.success(request, 'Thêm phương tiện thành công!')
            return redirect('guixe_list')
    else:
        form = GuiXeForm(hokhau_qs=hokhau_qs, disabled_hokhau=False)
    context = {'form': form}
    return render(request, 'apartment/guixe/form.html', context)


@login_required(login_url="login")
@role_required([1, 2])
def guixe_update(request, pk):
    guixe = get_object_or_404(GuiXe, pk=pk, is_deleted=False)
    hokhau_qs = get_hokhau_for_user(request)
    if guixe.hokhau not in hokhau_qs:
        messages.error(request, 'Không có quyền chỉnh sửa phương tiện này.')
        return redirect('guixe_list')
    if request.method == 'POST':
        post_data = request.POST.copy()
        # Nếu trường hokhau bị disabled thì không có trong POST, cần bổ sung thủ công
        if 'hokhau' not in post_data:
            post_data['hokhau'] = str(guixe.hokhau.pk)
        form = GuiXeForm(
            post_data,
            instance=guixe,
            hokhau_qs=hokhau_qs,
            disabled_hokhau=True,
            initial_hokhau=guixe.hokhau.pk
        )
        if form.is_valid():
            # Không cho đổi hộ khẩu khi edit
            obj = form.save(commit=False)
            obj.hokhau = guixe.hokhau
            obj.updated_by = request.user.username
            obj.save()
            messages.success(request, 'Cập nhật phương tiện thành công!')
            return redirect('guixe_list')
    else:
        form = GuiXeForm(
            instance=guixe,
            hokhau_qs=hokhau_qs,
            disabled_hokhau=True,
            initial_hokhau=guixe.hokhau.pk
        )
    context = {'form': form, 'guixe': guixe}
    return render(request, 'apartment/guixe/form.html', context)


@login_required(login_url="login")
@role_required([1, 2])
def guixe_delete(request, pk):
    guixe = get_object_or_404(GuiXe, pk=pk, is_deleted=False)
    hokhau_qs = get_hokhau_for_user(request)
    if guixe.hokhau not in hokhau_qs:
        messages.error(request, 'Không có quyền xóa phương tiện này.')
        return redirect('guixe_list')
    if request.method == 'POST':
        guixe.is_deleted = True
        guixe.updated_by = request.user.username
        guixe.save()
        messages.success(request, 'Đã xóa phương tiện!')
        return redirect('guixe_list')
    context = {'guixe': guixe}
    return render(request, 'apartment/guixe/confirm_delete.html', context)
