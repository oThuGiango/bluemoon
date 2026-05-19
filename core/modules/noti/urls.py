from django.urls import path
from . import views

urlpatterns = [
    path('thongbao/', views.thongbao_list, name='thongbao_list'),
    path('thongbao/create/', views.thongbao_create, name='thongbao_create'),
    path('thongbao/<int:pk>/', views.thongbao_detail, name='thongbao_detail'),
    path('thongbao/<int:pk>/update/',
         views.thongbao_update, name='thongbao_update'),
    path('thongbao/<int:pk>/delete/',
         views.thongbao_delete, name='thongbao_delete'),
]
