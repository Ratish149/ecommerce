from django.urls import path
from .views import ContactListCreateView, NewsLetterListCreateView

urlpatterns = [
    path('contact/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('newsletter/', NewsLetterListCreateView.as_view(),
         name='newsletter-list-create'),
]
