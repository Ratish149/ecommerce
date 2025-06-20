from django.db import models

# Create your models here.


class Banner(models.Model):
    BANNER_TYPE_CHOICES = [
        ('Slider', 'Slider'),
        ('Sidebar', 'Sidebar'),
        ('Banner', 'Banner'),
    ]
    banner_type = models.CharField(
        max_length=10, choices=BANNER_TYPE_CHOICES, default='Slider')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.banner_type


class BannerImage(models.Model):
    banner = models.ForeignKey(
        Banner, related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to='banners/', null=True, blank=True)
    image_alt_description = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.banner.banner_type
