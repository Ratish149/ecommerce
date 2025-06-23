from django.contrib import admin
from django.db import models
from .models import Product, ProductCategory, ProductImage, ProductSubCategory, Size, ProductReview, ProductSubSubCategory
from unfold.admin import ModelAdmin
from tinymce.widgets import TinyMCE


class SizeAdmin(ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class ProductCategoryAdmin(ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            return db_field.formfield(widget=TinyMCE())
        return super().formfield_for_dbfield(db_field, **kwargs)


class ProductSubSubCategoryAdmin(ModelAdmin):

    list_display = ('name', 'description')
    search_fields = ('name',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            return db_field.formfield(widget=TinyMCE())
        return super().formfield_for_dbfield(db_field, **kwargs)


class ProductSubCategoryAdmin(ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            return db_field.formfield(widget=TinyMCE())
        return super().formfield_for_dbfield(db_field, **kwargs)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    tab = True


class ProductAdmin(ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock',
                    'is_active', 'is_featured', 'is_popular')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    inlines = [ProductImageInline]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description' or db_field.name == 'highlight_description' or db_field.name == 'extra_description' or db_field.name == 'specifications':
            return db_field.formfield(widget=TinyMCE())
        return super().formfield_for_dbfield(db_field, **kwargs)


class ProductReviewAdmin(ModelAdmin):
    list_display = ('product', 'user', 'review', 'rating', 'created_at')
    list_filter = ('product', 'user')
    search_fields = ('product', 'user')
    ordering = ('-created_at',)


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductSubCategory, ProductSubCategoryAdmin)
admin.site.register(ProductSubSubCategory, ProductSubSubCategoryAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
