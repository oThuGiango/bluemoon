from django.urls import path
from . import views


urlpatterns = [
    path('hokhau/', views.hokhau_list, name='hokhau_list'),
    path('hokhau/<int:pk>/toggle-active/',
         views.hokhau_toggle_active, name='hokhau_toggle_active'),
    path('hokhau/add/', views.hokhau_add, name='hokhau_add'),
    path('hokhau/<int:pk>/', views.hokhau_detail, name='hokhau_detail'),
    path('hokhau/<int:pk>/edit/', views.hokhau_edit, name='hokhau_edit'),
    path('hokhau/<int:pk>/delete/', views.hokhau_delete, name='hokhau_delete'),

    path("demomanage", views.demomanage, name="demomanage"),
    path("demomanage/adddemo", views.add_demo, name="demomanage/adddemo"),
    path("demomanage/<int:id_nhankhau>/",
         views.nhan_khau_profile, name="nhan_khau_profile"),
    path("demomanage/delete/<int:id_nhankhau>/",
         views.nhan_khau_delete, name="nhan_khau_delete"),
    path("demomanage/<int:id_nhankhau>/edit/",
         views.edit_nhan_khau, name="edit_nhan_khau"),
    path("demomanage/dangkybiendongnhankhau/<int:id_nhankhau>/",
         views.dang_ky_bdbk, name="dang_ky_bdnk"),
    path("demomanage/biendongnhankhau",
         views.biendong_list, name="biendong_list"),
    path("demomanage/biendong/export/",
         views.export_biendong_excel, name="export_biendong_excel"),
    path("demomanage/export/", views.export_nhankhau_excel,
         name="export_nhankhau_excel"),


    path("hrmanage/export/", views.export_hokhau_excel,
         name="export_hokhau_excel"),
]
