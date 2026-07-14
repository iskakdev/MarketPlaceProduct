from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializers(serializers.ModelSerializer):
    product_image = ProductImageSerializers(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'
