from django.db import models
from django.utils.text import slugify
from accounts.models import User


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.FileField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.FileField(upload_to='products/')
    image_alt_description = models.TextField(blank=True, null=True)
    product = models.ForeignKey(
        'Product', related_name='images', on_delete=models.CASCADE)

    def __str__(self):
        return f"Image for {self.product.name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True, max_length=225)
    description = models.TextField(blank=True)
    market_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    thumbnail_image = models.FileField(
        upload_to='products/thumbnails/', null=True, blank=True)
    category = models.ForeignKey(
        ProductCategory, related_name='products', on_delete=models.CASCADE)
    is_popular = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=225, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        unique_together = ('name', 'category')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
