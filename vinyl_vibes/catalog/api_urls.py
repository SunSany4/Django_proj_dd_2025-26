from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'albums', api_views.AlbumViewSet)
router.register(r'comments', api_views.CommentViewSet)
router.register(r'users', api_views.UserViewSet)
router.register(r'orders', api_views.OrderViewSet, basename='orders')
router.register(r'cart', api_views.CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('auth/token/', api_views.CustomAuthToken.as_view(), name='api_token_auth'),
]