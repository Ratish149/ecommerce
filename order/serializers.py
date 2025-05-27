from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSmallSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSmallSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'product_id', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'full_name', 'order_number', 'status', 'shipping_address',
            'phone_number', 'email', 'total_amount', 'delivery_fee', 'city', 'state', 'zip_code',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        if 'items' in validated_data:
            items_data = validated_data.pop('items')
            # Delete existing items
            instance.items.all().delete()
            # Create new items
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class OrderItemSmallSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    product_slug = serializers.CharField(source='product.slug')
    product_thumbnail_image = serializers.SerializerMethodField()
    product_price = serializers.DecimalField(
        source='product.price', max_digits=10, decimal_places=2)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'product_slug', 'product_thumbnail_image', 'product_price',
                  'quantity', 'price', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price

    def get_product_thumbnail_image(self, obj):
        if obj.product.thumbnail_image:
            return f'/media/{obj.product.thumbnail_image.name}'
        return None


class OrderSmallSerializer(serializers.ModelSerializer):
    items = OrderItemSmallSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'full_name', 'order_number', 'status', 'shipping_address', 'city', 'state', 'zip_code',
                  'phone_number', 'email', 'total_amount', 'delivery_fee', 'items',
                  'created_at', 'updated_at']
