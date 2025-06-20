from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Banner, BannerImage

# Register your models here.


class BannerImageInline(TabularInline):
    model = BannerImage
    extra = 1
    tab = True


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ['banner_type', 'is_active']
    inlines = [BannerImageInline]
