from django.urls import path
from .views import OrderView, OrderDetailView

urlpatterns = [
    path('orders/', OrderView.as_view(), name='order-list'),
    path('orders/<str:order_number>/',
         OrderDetailView.as_view(), name='order-detail'),
]
