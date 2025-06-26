from django.urls import path
from .views import BannerListCreateView, BannerRetrieveUpdateDestroyView, BannerImageListCreateView, BannerImageRetrieveUpdateDestroyView, PopUpCreateView, PopUpFormCreateView, PopUpRetrieveUpdateDestroyView, PopUpFormRetrieveUpdateDestroyView

urlpatterns = [
    path('banner-images/', BannerImageListCreateView.as_view(),
         name='banner-image-list-create'),
    path('banner-images/<int:pk>/', BannerImageRetrieveUpdateDestroyView.as_view(),
         name='banner-image-retrieve-update-destroy'),
    path('banners/', BannerListCreateView.as_view(), name='banner-list-create'),
    path('banners/<int:pk>/', BannerRetrieveUpdateDestroyView.as_view(),
         name='banner-retrieve-update-destroy'),
    path('popup/', PopUpCreateView.as_view(), name='popup-create'),
    path('popupform/', PopUpFormCreateView.as_view(),
         name='popupform-create'),
    path('popup/<int:pk>/', PopUpRetrieveUpdateDestroyView.as_view(),
         name='popup-retrieve-update-destroy'),
    path('popupform/<int:pk>/', PopUpFormRetrieveUpdateDestroyView.as_view(),
         name='popupform-retrieve-update-destroy'),
]
