"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from catalog import views as catalog_views
from users import views as users_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # URLs для альбомов
    path('admin/', admin.site.urls),
    path('', catalog_views.album_list, name='album_list'),
    path('album/<int:pk>/', catalog_views.album_detail, name='album_detail'),
    path('add/', catalog_views.album_create, name='album_create'),
    path('edit/<int:pk>/', catalog_views.album_edit, name='album_edit'),
    path('delete/<int:pk>/', catalog_views.album_delete, name='album_delete'),
    path('comment/create/<int:album_pk>/', catalog_views.comment_create, name='comment_create'),
    path('comment/delete/<int:comment_pk>/', catalog_views.comment_delete, name='comment_delete'),
    path('cart/', catalog_views.cart_view, name='cart_view'),
    path('cart/add/<int:album_id>/', catalog_views.add_cart, name='cart_add'),
    path('cart/remove/<int:album_id>/', catalog_views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', catalog_views.cart_update, name='cart_update'),
    path('checkout/', catalog_views.checkout_view, name='checkout'),
    path('orders', catalog_views.orders_list, name='orders_list'),
    path('order/<int:order_id>/', catalog_views.order_detail, name='order_detail'),
    #Экспорт и статистика
    path('export/orders/excel', catalog_views.export_orders_excel, name='export_orders_excel'),
    path('export/orders/csv', catalog_views.export_orders_csv, name='export_orders_csv'),
    path('export/orders/pdf/<int:order_id>', catalog_views.export_order_pdf, name='export_order_pdf'),
    path('export/orders/pdf/', catalog_views.export_orders_pdf, name='export_orders_pdf'),
    path('statistics/', catalog_views.statistics_dashboard, name='statistics_dashboard'),
    # URLs для аутентификации
    path('register/', users_views.register, name='register'),
    path('login/',users_views.user_login, name='login'),
    path('logout/', users_views.user_logout, name='logout'),
    path('profile/', users_views.profile, name='profile'),
    #API URLs
    path('api/', include('catalog.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
