from django.urls import path

from . import views

urlpatterns = [
    path("fee_management/", views.fee_management, name="fee_management"),
    path("fee_management/add/", views.add_khoanthu, name="add_khoanthu"),
    path("fee_management/edit/<int:pk>/",
         views.edit_khoanthu, name="edit_khoanthu"),
    path("fee_management/delete/<int:pk>/",
         views.delete_khoanthu, name="delete_khoanthu"),
    path("fee_management/detail/<int:pk>/modal/",
         views.view_khoanthu_detail_modal, name="view_khoanthu_detail_modal"),

    #     Kỳ thu
    path("fee_collection_period/", views.fee_collection_period,
         name="fee_collection_period"),
    path("fee_collection_period/add/", views.add_dotthu, name="add_dotthu"),
    path("fee_collection_period/edit/<int:pk>/",
         views.edit_dotthu, name="edit_dotthu"),
    path("fee_collection_period/delete/<int:pk>/",
         views.delete_dotthu, name="delete_dotthu"),
    path("fee_collection_period/detail/<int:pk>/modal/",
         views.view_dotthu_detail_modal, name="view_dotthu_detail_modal"),

    #     Hóa đơn
    path("update_payment_status/", views.update_payment_status,
         name="update_payment_status"),
    path("create_invoices/", views.create_invoices_for_period,
         name="create_invoices_for_period"),
    path("statistics_view/", views.statistics_view, name="statistics_view"),
    path("statistics/export/", views.export_finance_excel,
         name="export_finance_excel"),
    path("invoice_history/", views.invoice_history, name="invoice_history"),
    path("invoice_history/detail/<int:pk>/modal/",
         views.view_invoice_detail_modal, name="view_invoice_detail_modal"),
    path("invoice_history/delete/<int:pk>/",
         views.delete_invoice_modal, name="delete_invoice_modal"),
]
