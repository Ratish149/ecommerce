from django.urls import path
from .views import BannerListCreateView, BannerRetrieveUpdateDestroyView, BannerImageListCreateView, BannerImageRetrieveUpdateDestroyView

urlpatterns = [
    path('banner-images/', BannerImageListCreateView.as_view(),
         name='banner-image-list-create'),
    path('banner-images/<int:pk>/', BannerImageRetrieveUpdateDestroyView.as_view(),
         name='banner-image-retrieve-update-destroy'),
    path('banners/', BannerListCreateView.as_view(), name='banner-list-create'),
    path('banners/<int:pk>/', BannerRetrieveUpdateDestroyView.as_view(),
         name='banner-retrieve-update-destroy'),
]
