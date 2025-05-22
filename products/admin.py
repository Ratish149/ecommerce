from django.contrib import admin
from django.db import models
from .models import Product, ProductCategory, ProductImage
from unfold.admin import ModelAdmin
from tinymce.widgets import TinyMCE


class ProductCategoryAdmin(ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    tab = True


class ProductAdmin(ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    inlines = [ProductImageInline]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
