from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'products', api_views.ProductViewSet)
router.register(r'categories', api_views.CategoryViewSet)
router.register(r'orders', api_views.OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/login', api_views.Login.as_view(), name='api_login'),
    path('api/logout', api_views.Logout.as_view(), name='api_logout'),
    path('', views.home, name='home'),
    path('products/', views.all_products, name='all_products'),
    path('products/<str:category>/', views.all_products, name='all_products_cat'),
    path('search/', views.search, name='search'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/data/', views.cart_data, name='cart_data'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/confirm/', views.confirm_order, name='confirm_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.orders, name='orders'),
    path('change-password/', views.change_password, name='change_password'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
]
