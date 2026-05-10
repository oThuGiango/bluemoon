from django.urls import path

from . import views

urlpatterns = [
    # API cho phần căn hộ
    path("canho/", views.canho_list, name="canho_list"),
    path("canho/add/", views.canho_add, name="canho_add"),
    path("canho/<int:id_canho>/", views.canho_detail, name="canho_detail"),
    path("canho/<int:id_canho>/edit/", views.canho_edit, name="canho_edit"),
    path("canho/<int:id_canho>/delete/",
         views.canho_delete, name="canho_delete"),
]


# Building URLs
urlpatterns += [
    path("building/", views.building_list, name="building_list"),
    path("building/add/", views.building_add, name="building_add"),
    path("building/<int:id>/edit/", views.building_edit, name="building_edit"),
    path("building/<int:id>/delete/",
         views.building_delete, name="building_delete"),
    path("building/<int:id>/", views.building_detail, name="building_detail"),
]
