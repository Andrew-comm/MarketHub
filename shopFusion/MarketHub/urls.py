
from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.display_two_products, name='products'),
    path('category/<int:category_id>/', views.product_list_by_category, name='product_list_by_category'),
    path('category/<int:category_id>/subcategory/<int:subcategory_id>/', views.product_list_by_subcategory, name='product_list_by_subcategory'),
    
    
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),

   

]

