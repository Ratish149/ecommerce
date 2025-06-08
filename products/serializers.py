from rest_framework import serializers
from accounts.models import User
from accounts.serializers import UserSerializer
from .models import Product, ProductCategory, ProductImage, Wishlist, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None

class ProductImageSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['__all__']

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if request and request.method == 'GET':
            return f'/media/{obj.image.name}'
        return obj.image.url if obj.image else None


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        write_only=True,
        source='category'
    )
    thumbnail_image = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_thumbnail_image(self, obj):
        if obj.thumbnail_image:
            return f'/media/{obj.thumbnail_image.name}'
        return None

    def get_is_wishlisted(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        user = self.context.get('request').user
        if user:
            return Wishlist.objects.filter(user=user, product=obj).exists()
        return False

    def create(self, validated_data):
        request = self.context.get('request')
        images_data = request.FILES.getlist('images') if request else []
        thumbnail_image = request.FILES.get(
            'thumbnail_image') if request else None

        # Create product with thumbnail image if provided
        if thumbnail_image:
            validated_data['thumbnail_image'] = thumbnail_image

        product = Product.objects.create(**validated_data)

        # Create product images
        for image_file in images_data:
            ProductImage.objects.create(
                product=product, image=image_file, name=image_file.name)
        return product
    
    def update(self, instance, validated_data):
        images_data = self.context.get('request').FILES.getlist('images')
        thumbnail_image = self.context.get('request').FILES.get('thumbnail_image')

        # Update product with thumbnail image if provided
        if thumbnail_image:
            if instance.thumbnail_image:
                instance.thumbnail_image.delete()
            instance.thumbnail_image = thumbnail_image

        instance = super().update(instance, validated_data)

        # Update product images
        instance.images.all().delete()
        for image_file in images_data:
            ProductImage.objects.create(
                product=instance, image=image_file, name=image_file.name)
        return instance


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    thumbnail_image = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_thumbnail_image(self, obj):
        if obj.thumbnail_image:
            return f'/media/{obj.thumbnail_image.name}'
        return None
    


class ProductSmallSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'market_price',
                  'price', 'thumbnail_image', 'meta_title', 'meta_description', 'category']


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSmallSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product',
                  'product_id', 'created_at', 'updated_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    product = ProductSmallSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product_id', 'user_id', 'product', 'user', 'review',
                  'rating', 'created_at', 'updated_at']


class ProductReviewDetailSerializer(serializers.ModelSerializer):
    product = ProductSmallSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'review',
                  'rating', 'created_at', 'updated_at']
