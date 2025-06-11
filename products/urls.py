from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    CategoryListCreateView,
    CategoryDetailView,
    SimilarProductsView,
    WishlistListCreateView,
    WishlistRetrieveUpdateDestroyView,
    ProductReviewView,
    ProductImageListCreateView,
    ProductImageRetrieveUpdateDestroyView,
    ProductReviewRetrieveUpdateDestroyView
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<slug:slug>/similar/',
         SimilarProductsView.as_view(), name='similar-products'),
    path('products/<slug:category_slug>/<slug:slug>/',
         ProductDetailView.as_view(), name='product-detail'),
    path('images/', ProductImageListCreateView.as_view(),
         name='product-image-list-create'),
    path('images/<int:id>/', ProductImageRetrieveUpdateDestroyView.as_view(),
         name='product-image-retrieve-update-destroy'),
    path('categories/', CategoryListCreateView.as_view(),
         name='category-list-create'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(),
         name='category-detail'),
    path('wishlist/', WishlistListCreateView.as_view(),
         name='wishlist-list-create'),
    path('wishlist/<int:id>/', WishlistRetrieveUpdateDestroyView.as_view(),
         name='wishlist-retrieve-update-destroy'),
    path('product-reviews/',
         ProductReviewView.as_view(), name='product-review'),
    path('product-reviews/<int:id>/', ProductReviewRetrieveUpdateDestroyView.as_view(),
         name='product-review-retrieve-update-destroy'),
]
