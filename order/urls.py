from django.urls import path
from .views import (
    OrderView, OrderDetailView, DashboardStats,
    MyOrderView, RevenueView, MyOrderStatusView
)

urlpatterns = [
    path('orders/', OrderView.as_view(), name='order-list'),
    path('orders/<str:order_number>/',
         OrderDetailView.as_view(), name='order-detail'),
    path('my-orders/', MyOrderView.as_view(), name='my-order-list'),
    path('my-order-status/', MyOrderStatusView.as_view(), name='my-order-status'),
    path('dashboard-stats/', DashboardStats.as_view(), name='dashboard-stats'),
    path('revenue/', RevenueView.as_view(), name='order-revenue'),
]
