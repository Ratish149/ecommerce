from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer, OrderSmallSerializer
from products.models import Product
from django.db.models import Sum

# Create your views here.


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSmallSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.user)
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


class MyOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSmallSerializer(orders, many=True)
        return Response(serializer.data)
