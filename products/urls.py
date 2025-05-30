from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    CategoryListCreateView,
    CategoryDetailView,
    SimilarProductsView
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<slug:slug>/similar/',
         SimilarProductsView.as_view(), name='similar-products'),
    path('products/<slug:category_slug>/<slug:slug>/',
         ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListCreateView.as_view(),
         name='category-list-create'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(),
         name='category-detail'),
]
