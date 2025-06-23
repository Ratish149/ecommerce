from django.shortcuts import render
from rest_framework import generics
from .models import Contact, NewsLetter
from .serializers import ContactSerializer, NewsLetterSerializer
# Create your views here.


class ContactListCreateView(generics.ListCreateAPIView):
    queryset = Contact.objects.only(
        'id', 'first_name', 'last_name', 'email', 'message', 'created_at')
    serializer_class = ContactSerializer


class NewsLetterListCreateView(generics.ListCreateAPIView):
    queryset = NewsLetter.objects.only(
        'id', 'email', 'created_at')
    serializer_class = NewsLetterSerializer
