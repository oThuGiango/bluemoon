from django.urls import path

from . import views

urlpatterns = [
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
    path("hrmanage/", views.hrmanage, name="hrmanage"),
    path("hrmanage/them/", views.add_hokhau, name="add_hokhau"),
    path("hrmanage/detail/<int:id_hokhau>/",
         views.hokhau_detail, name="hokhau_detail"),
    path("hrmanage/<int:id_hokhau>/edit/",
         views.edit_hokhau, name="hokhau_edit"),
    path("hrmanage/<int:id_hokhau>/delete/",
         views.hrmanage_delete, name="hrmanage_delete"),
    path("hrmanage/export/", views.export_hokhau_excel,
         name="export_hokhau_excel"),
]
