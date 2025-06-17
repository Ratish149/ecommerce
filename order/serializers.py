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
    color = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'product_id', 'quantity', 'price', 'color']


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
            product = item_data['product']
            quantity = item_data['quantity']
            color = item_data.get('color')

            if color:
                # Check color-specific stock with case-insensitive matching
                product_image = product.images.filter(
                    color__name__icontains=color).first()
                if not product_image:
                    raise serializers.ValidationError(
                        f"Color {color} not available for product {product.name}")

                if product_image.stock < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for product {product.name} in color {color}")

                # Decrease color-specific stock
                product_image.stock -= quantity
                product_image.save()
            else:
                # Check overall product stock
                if product.stock < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for product {product.name}")

                # Decrease overall product stock
                product.stock -= quantity
                product.save()

            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        if 'items' in validated_data:
            items_data = validated_data.pop('items')

            # Restore stock from existing items before deleting them
            for existing_item in instance.items.all():
                product = existing_item.product
                if existing_item.color:
                    product_image = product.images.filter(
                        color__name__icontains=existing_item.color).first()
                    if product_image:
                        product_image.stock += existing_item.quantity
                        product_image.save()
                else:
                    product.stock += existing_item.quantity
                    product.save()

            # Delete existing items
            instance.items.all().delete()

            # Create new items and decrease stock
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                color = item_data.get('color')

                if color:
                    # Check color-specific stock with case-insensitive matching
                    product_image = product.images.filter(
                        color__name__icontains=color).first()
                    if not product_image:
                        raise serializers.ValidationError(
                            f"Color {color} not available for product {product.name}")

                    if product_image.stock < quantity:
                        raise serializers.ValidationError(
                            f"Insufficient stock for product {product.name} in color {color}")

                    # Decrease color-specific stock
                    product_image.stock -= quantity
                    product_image.save()
                else:
                    # Check overall product stock
                    if product.stock < quantity:
                        raise serializers.ValidationError(
                            f"Insufficient stock for product {product.name}")

                    # Decrease overall product stock
                    product.stock -= quantity
                    product.save()

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
