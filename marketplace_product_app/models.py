from django.db import models


class Category(models.Model):
    category_image = models.ImageField(null=True, blank=True)
    category_name = models.CharField(max_length=67)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    article_number = models.PositiveIntegerField(unique=True)
    is_official = models.BooleanField()
    video = models.FileField(null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.IntegerField()

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    product_image = models.ImageField(upload_to='product_images/')
