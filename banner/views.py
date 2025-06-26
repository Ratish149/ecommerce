from django.shortcuts import render
from rest_framework import generics
from .models import Banner, BannerImage, PopUp, PopUpForm
from .serializers import BannerSerializer, BannerImageSerializer, PopUpSerializer, PopUpFormSerializer

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


class PopUpCreateView(generics.ListCreateAPIView):
    queryset = PopUp.objects.filter(is_active=True)
    serializer_class = PopUpSerializer


class PopUpRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PopUp.objects.filter(is_active=True)
    serializer_class = PopUpSerializer


class PopUpFormCreateView(generics.ListCreateAPIView):
    queryset = PopUpForm.objects.all()
    serializer_class = PopUpFormSerializer


class PopUpFormRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PopUpForm.objects.all()
    serializer_class = PopUpFormSerializer
