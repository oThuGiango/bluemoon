from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.user_logout, name="logout"),
    path("", views.home, name="home"),
    path("admin_home", views.admin_home, name="admin_home"),
    path("accountant_home/", views.accountant_home, name="accountant_home"),
    path("test/", views.test, name="test"),
]
