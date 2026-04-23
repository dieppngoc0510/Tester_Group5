from django.urls import path
from . import views

urlpatterns = [
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/orders/', views.admin_orders, name='admin_orders'),
    path('panel/orders/detail/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('panel/orders/create/', views.admin_create_order, name='admin_create_order'),
    path('panel/orders/edit/<int:order_id>/', views.admin_edit_order, name='admin_edit_order'),
    path('panel/orders/delete/<int:order_id>/', views.admin_delete_order, name='admin_delete_order'),
    path('panel/orders/update-status/<int:order_id>/', views.admin_update_order_status, name='admin_update_order_status'),
    path('panel/api/customer-info/', views.get_customer_info, name='get_customer_info'),
]
