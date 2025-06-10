from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer, OrderSmallSerializer
from products.models import Product
from django.db.models import Sum, Count
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, ListCreateAPIView
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters
from django.utils import timezone
from django.db import models
# Create your views here.


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(
        field_name='full_name', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(
        field_name='phone_number', lookup_expr='icontains')
    status = django_filters.CharFilter(
        field_name='status', lookup_expr='icontains')
    order_number = django_filters.CharFilter(
        field_name='order_number', lookup_expr='icontains')
    # Date range filters
    date_gte = django_filters.DateFilter(
        field_name='created_at', lookup_expr='gte')
    date_lte = django_filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['full_name', 'phone_number', 'order_number',
                  'status', 'date_gte', 'date_lte']


class OrderView(ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSmallSerializer
    filter_backends = [DjangoFilterBackend,
                       rest_filters.SearchFilter, rest_filters.OrderingFilter]
    search_fields = ['phone_number', 'full_name', 'order_number']
    filterset_class = OrderFilter
    pagination_class = CustomPagination
    ordering = ['-created_at', 'created_at']

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            serializer = OrderSmallSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):

    def get_object(self, order_number):
        try:
            return Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return None

    def get(self, request, order_number):
        order = self.get_object(order_number)
        if not order:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, order_number):
        order = self.get_object(order_number)
        if not order:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_number):
        order = self.get_object(order_number)
        if not order:
            return Response(status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardStats(APIView):

    def get(self, request):

        # Get total products
        total_products = Product.objects.count()

        # Get total orders
        total_orders = Order.objects.count()

        # Get pending orders
        pending_orders = Order.objects.filter(status='pending').count()

        # Get total revenue (sum of total_amount from all orders)
        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount'))['total'] or 0

        stats = {
            'total_products': total_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': float(total_revenue)
        }

        return Response(stats)


class MyOrderFilter(django_filters.FilterSet):
    order_number = django_filters.CharFilter(
        field_name='order_number', lookup_expr='icontains')
    date_gte = django_filters.DateFilter(
        field_name='created_at', lookup_expr='gte')
    date_lte = django_filters.DateFilter(
        field_name='created_at', lookup_expr='lte')
    status = django_filters.CharFilter(
        field_name='status', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['order_number', 'date_gte', 'date_lte', 'status']


class MyOrderView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,
                       rest_filters.SearchFilter, rest_filters.OrderingFilter]
    search_fields = ['order_number', 'items__product__name']
    filterset_class = MyOrderFilter
    serializer_class = OrderSmallSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class RevenueView(ListAPIView):

    def get(self, request):
        filter_type = request.GET.get('filter', 'daily')  # Default to daily
        today = timezone.now().date()

        try:
            # Base queryset - all orders
            base_queryset = Order.objects.all()

            if filter_type == 'daily':
                revenue = (
                    base_queryset.filter(
                        created_at__year=today.year,
                        created_at__month=today.month
                    )
                    .values('created_at__date')
                    .annotate(
                        period=models.F('created_at__date'),
                        total_revenue=Sum('total_amount', default=0),
                        order_count=Count('id')
                    )
                    .order_by('period')
                )

            elif filter_type == 'weekly':
                revenue = (
                    base_queryset.filter(created_at__year=today.year)
                    .annotate(period=TruncWeek('created_at'))
                    .values('period')
                    .annotate(
                        total_revenue=Sum('total_amount', default=0),
                        order_count=Count('id')
                    )
                    .order_by('period')
                )

            elif filter_type == 'yearly':
                revenue = (
                    base_queryset.annotate(period=TruncYear('created_at'))
                    .values('period')
                    .annotate(
                        total_revenue=Sum('total_amount', default=0),
                        order_count=Count('id')
                    )
                    .order_by('period')
                )

            else:  # Default is monthly
                revenue = (
                    base_queryset.annotate(period=TruncMonth('created_at'))
                    .values('period')
                    .annotate(
                        total_revenue=Sum('total_amount', default=0),
                        order_count=Count('id')
                    )
                    .order_by('period')
                )

            # Format the response data
            response_data = [{
                'period': entry['period'].strftime('%Y-%m-%d') if filter_type == 'daily'
                else entry['period'].strftime(
                    '%Y-%m-%d' if filter_type == 'weekly'
                    else '%Y-%m' if filter_type == 'monthly'
                    else '%Y'
                ),
                'total_revenue': float(entry['total_revenue']),
                'order_count': entry['order_count']
            } for entry in revenue]

            return Response({
                'filter_type': filter_type,
                'data': response_data
            })

        except Exception as e:
            return Response(
                {'error': f'Failed to fetch revenue data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
