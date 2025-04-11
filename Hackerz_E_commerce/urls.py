from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('category/<slug:category_slug>/', views.category_view, name='category_view'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/count/', views.cart_count, name='cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/product/add/', views.add_product, name='add_product'),
    path('vendor/product/<int:product_id>/', views.vendor_product_detail, name='vendor_product_detail'),
    path('vendor/product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('vendor/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
] 