from django.shortcuts import render
from rest_framework import generics
from .models import Banner, BannerImage
from .serializers import BannerSerializer, BannerImageSerializer

# Create your views here.


class BannerImageListCreateView(generics.ListCreateAPIView):
    queryset = BannerImage.objects.all()
    serializer_class = BannerImageSerializer


class BannerImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BannerImage.objects.all()
    serializer_class = BannerImageSerializer


class BannerListCreateView(generics.ListCreateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


class BannerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
