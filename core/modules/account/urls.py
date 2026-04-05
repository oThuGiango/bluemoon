from django.urls import path

from . import views

urlpatterns = [
    path("accountmanage", views.accountmanage, name="accountmanage"),
    path("accountmanage/addaccount", views.accountmanage_addaccount,
         name="accountmanage_addaccount"),
    path("accountmanage/addaccount/",
         views.accountmanage_addaccount, name="addaccount"),
    path("accountmanage/change/<int:id_taikhoan>/",
         views.edit_taikhoan, name="edit_taikhoan"),
    path("accountmanage/view/<int:id_taikhoan>/",
         views.view_taikhoan, name="view_taikhoan"),
    path("accountmanage/delete/<int:id_taikhoan>/",
         views.accountmanage_delete, name="accountmanage_delete"),
]
