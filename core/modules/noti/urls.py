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

    path('ticket/', views.ticket_list, name='ticket_list'),
    path('ticket/create/', views.ticket_create, name='ticket_create'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:pk>/assign/', views.ticket_assign, name='ticket_assign'),
    path('ticket/<int:pk>/status/', views.ticket_status, name='ticket_status'),
    path('ticket/<int:pk>/response/',
         views.ticket_response, name='ticket_response'),
    path('ticket/<int:pk>/review/', views.ticket_review, name='ticket_review'),
    path('ticket/<int:pk>/delete/', views.ticket_delete, name='ticket_delete'),
]
