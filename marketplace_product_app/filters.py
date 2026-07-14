from django_filters import FilterSet
from .models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'product_name': ['exact'],
            'article_number': ['exact'],
            'is_official': ['exact'],
            'price': ['gt', 'lt']
        }