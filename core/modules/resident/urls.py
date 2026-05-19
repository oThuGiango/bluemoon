from . import views
from django.urls import path

urlpatterns = [
    # Hộ khẩu
    path('hokhau/', views.hokhau_list, name='hokhau_list'),
    path('hokhau/<int:pk>/toggle-active/',
         views.hokhau_toggle_active, name='hokhau_toggle_active'),
    path('hokhau/add/', views.hokhau_add, name='hokhau_add'),
    path('hokhau/<int:pk>/', views.hokhau_detail, name='hokhau_detail'),
    path('hokhau/<int:pk>/edit/', views.hokhau_edit, name='hokhau_edit'),
    path('hokhau/<int:pk>/delete/', views.hokhau_delete, name='hokhau_delete'),

    # Nhân khẩu
    path('nhankhau/', views.nhankhau_list, name='nhankhau_list'),
    path('nhankhau/add/', views.nhankhau_add, name='nhankhau_add'),
    path('nhankhau/<int:pk>/', views.nhankhau_detail, name='nhankhau_detail'),
    path('nhankhau/<int:pk>/edit/', views.nhankhau_edit, name='nhankhau_edit'),
    path('nhankhau/<int:pk>/delete/',
         views.nhankhau_delete, name='nhankhau_delete'),

    # Biến động nhân khẩu
    path("biendongnhankhau/",
         views.biendong_list, name="biendong_list"),
    path("biendongnhankhau/<int:id_nhankhau>/",
         views.dang_ky_bdnk, name="dang_ky_bdnk"),
    path("biendongnhankhau/<int:id_biendong>/delete/",
         views.biendong_delete, name="biendong_delete"),

    # Xuất Excel
    path("hokhau/export/", views.export_hokhau_excel,
         name="export_hokhau_excel"),
    path("nhankhau/export/", views.export_nhankhau_excel,
         name="export_nhankhau_excel"),
    path("biendongnhankhau/export/",
         views.export_biendong_excel, name="export_biendong_excel"),
]
