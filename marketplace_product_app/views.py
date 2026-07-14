from .serializers import CategorySerializers, ProductSerializers, ProductImageSerializers
from .models import Category, Product, ProductImage
from rest_framework import viewsets
from .filters import ProductFilter
from .pagination import ProductPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializers


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['product_name']
    ordering_fields = ['price']
    pagination_class = ProductPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.id)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializers