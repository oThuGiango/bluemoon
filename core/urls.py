from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    # path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.user_logout, name="logout"),

    path('', views.home, name='home'),
    path('admin_home', views.admin_home, name='admin_home'),
    path('accountmanage', views.accountmanage, name='accountmanage'),
    path('accountmanage/addaccount', views.accountmanage_addaccount, name='accountmanage_addaccount'),
    # alias:
    path('accountmanage/addaccount/', views.accountmanage_addaccount, name='addaccount'),
    path('accountmanage/change/<int:id_taikhoan>/', views.edit_taikhoan, name='edit_taikhoan'),
    path('accountmanage/view/<int:id_taikhoan>/', views.view_taikhoan, name='view_taikhoan'),  
    path('accountmanage/delete/<int:id_taikhoan>/', views.accountmanage_delete, name='accountmanage_delete'),  


    path('demomanage', views.demomanage, name='demomanage'),
    path('demomanage/adddemo', views.add_demo, name='demomanage/adddemo'),
    path('demomanage/<int:id_nhankhau>/', views.nhan_khau_profile, name='nhan_khau_profile'),
    path('demomanage/delete/<int:id_nhankhau>/', views.nhan_khau_delete, name='nhan_khau_delete'),
    path('demomanage/<int:id_nhankhau>/edit/', views.edit_nhan_khau, name='edit_nhan_khau'),  
    path('demomanage/dangkybiendongnhankhau/<int:id_nhankhau>/', views.dang_ky_bdbk, name='dang_ky_bdnk'),
    path('demomanage/biendongnhankhau', views.biendong_list, name='biendong_list'),
    path('demomanage/biendong/export/',views.export_biendong_excel,name='export_biendong_excel'),
    path('demomanage/export/',views.export_nhankhau_excel,name='export_nhankhau_excel'),


    path('test/', views.test, name='test'),
 #   path('login/', views.login, name='login'),

    path('hrmanage/', views.hrmanage, name='hrmanage'),
    path('hrmanage/them/', views.add_hokhau, name='add_hokhau'),
    path('hrmanage/detail/<int:id_hokhau>/', views.hokhau_detail, name='hokhau_detail'),
    path('hrmanage/<int:id_hokhau>/edit/', views.edit_hokhau, name='hokhau_edit'),
    path('hrmanage/<int:id_hokhau>/delete/', views.hrmanage_delete, name='hrmanage_delete'),
    path('hrmanage/export/', views.export_hokhau_excel, name='export_hokhau_excel'),
    #============Kế toán URLs===================
    path('accountant_home/', views.accountant_home, name='accountant_home'),  # Accountant main page

    path('fee_management/', views.fee_management, name='fee_management'),  # Trang quản lý khoản thu
    path('fee_management/add/', views.add_khoanthu, name='add_khoanthu'),
    path('fee_management/edit/<int:pk>/',views.edit_khoanthu, name = 'edit_khoanthu'),
    path('fee_management/delete/<int:pk>/', views.delete_khoanthu, name='delete_khoanthu'),
    path('fee_management/detail/<int:pk>/modal/', views.view_khoanthu_detail_modal, name='view_khoanthu_detail_modal'), 


    path('fee_collection_period/', views.fee_collection_period, name='fee_collection_period'),  # Trang quản lý đợt thu phí
    path('fee_collection_period/add/', views.add_dotthu, name='add_dotthu'),
    path('fee_collection_period/edit/<int:pk>/', views.edit_dotthu, name='edit_dotthu'),
    path('fee_collection_period/delete/<int:pk>/', views.delete_dotthu, name='delete_dotthu'),
    path('fee_collection_period/detail/<int:pk>/modal/', views.view_dotthu_detail_modal, name='view_dotthu_detail_modal'),
    path('update_payment_status/', views.update_payment_status, name='update_payment_status'),
    path('create_invoices/', views.create_invoices_for_period, name='create_invoices_for_period'),
        
    path('statistics_view/', views.statistics_view, name='statistics_view'),  # Trang thống kê
    path('statistics/export/', views.export_finance_excel, name='export_finance_excel'),

    path('invoice_history/',views.invoice_history, name='invoice_history'),  # Trang lịch sử hóa đơn
    path('invoice_history/detail/<int:pk>/modal/', views.view_invoice_detail_modal, name='view_invoice_detail_modal'),
    path('invoice_history/delete/<int:pk>/', views.delete_invoice_modal, name='delete_invoice_modal'),
]
