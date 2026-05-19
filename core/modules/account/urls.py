from django.urls import path

from . import views

urlpatterns = [
    path("accountmanage", views.accountmanage, name="accountmanage"),
    path("account/add", views.add_account,
         name="add_account"),
    path("account/edit/<int:id_taikhoan>/",
         views.edit_account, name="edit_account"),
    path("account/detail/<int:pk>/modal/",
         views.view_account, name="view_account"),
    path("account/delete/<int:id_taikhoan>/",
         views.delete_account, name="delete_account"),
    path("account/deactivate/<int:pk>/",
         views.deactivate_account, name="deactivate_account"),
    path("account/change-password/", views.change_password, name="change_password"),
]
