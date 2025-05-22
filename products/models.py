from django.db import models
from django.utils.text import slugify


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.FileField(upload_to='products/')
    product = models.ForeignKey(
        'Product', related_name='images', on_delete=models.CASCADE)

    def __str__(self):
        return f"Image for {self.product.name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(blank=True)
    market_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(
        ProductCategory, related_name='products', on_delete=models.CASCADE)
    is_popular = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
