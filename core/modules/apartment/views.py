from core.forms import CanHoForm
from django.contrib import messages
from core.decorators import role_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import CanHo, Building
from core.modules.resident.models import HoKhau


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
    canho_list = CanHo.objects.filter(
        is_deleted=False).order_by("-id_canho")

    query = request.GET.get("search_canho", "")
    status = request.GET.get('status')
    apartment_type = request.GET.get('type')

    if apartment_type:
        canho_list = canho_list.filter(apartment_type=apartment_type)
    if status:
        canho_list = canho_list.filter(status=status)

    if query:
        canho_list = canho_list.filter(so_can_ho__icontains=query)
    total_count = canho_list.count()
    context = {"canho_list": canho_list,
               "query": query, "status": status, "type": apartment_type, "total_count": total_count}
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
            messages.error(request, "Vui lòng kiểm tra lại các trường!")
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
