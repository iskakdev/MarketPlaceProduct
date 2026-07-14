from .views import CategoryViewSet, ProductViewSet, ProductImageViewSet
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product_images', ProductImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]