from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Product, ProductCategory, ProductImage, ProductSubSubCategory, Wishlist, ProductReview, ProductSubCategory, Size, Color, ProductSubSubCategory
from django.db.models import Avg
from rest_framework.validators import UniqueTogetherValidator


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


class CategorySmallSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'image']

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductSubCategory
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


class SubCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = ['id', 'name', 'slug']


class SubCategorySmallSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category = CategorySmallSerializer(read_only=True)

    class Meta:
        model = ProductSubCategory
        fields = ['id', 'name', 'slug', 'description', 'image', 'category']

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


class SubSubCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubSubCategory
        fields = ['id', 'name', 'slug',]


class SubSubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategory_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductSubCategory.objects.all(),
        write_only=True,
        source='subcategory',
        required=False,
        allow_null=True
    )

    class Meta:
        model = ProductSubSubCategory
        fields = ['id', 'name', 'slug', 'description',
                  'image', 'subcategory_id']

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


class SubSubCategorySmallSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategory = SubCategoryListSerializer(read_only=True)

    class Meta:
        model = ProductSubSubCategory
        fields = ['id', 'name', 'slug', 'subcategory', 'image', 'description']

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'description']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'description']


class ProductImageSmallSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_alt_description',
                  'color', 'stock', 'product']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request and request.method == 'GET':
                return f'/media/{obj.image.name}'
            return obj.image.url
        return None


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_alt_description',
                  'color', 'stock', 'product', 'is_in_stock']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request and request.method == 'GET':
                return f'/media/{obj.image.name}'
            return obj.image.url
        return None

    def get_is_in_stock(self, obj):
        return obj.stock > 0 if obj.stock is not None else False


class ProductSerializer(serializers.ModelSerializer):
    size = SizeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySmallSerializer(read_only=True)
    subcategory = SubCategorySmallSerializer(read_only=True)
    subsubcategory = SubSubCategorySmallSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        write_only=True,
        source='category',
        required=False,
        allow_null=True
    )
    subcategory_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductSubCategory.objects.all(),
        write_only=True,
        source='subcategory',
        required=False,
        allow_null=True
    )
    subsubcategory_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductSubSubCategory.objects.all(),
        write_only=True,
        source='subsubcategory',
        required=False,
        allow_null=True
    )
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(),
        write_only=True,
        source='size',
        many=True,
        required=False,
        allow_null=True
    )
    thumbnail_image = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields=['name', 'subsubcategory_id']
            )
        ]

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
        thumbnail_image = request.FILES.get(
            'thumbnail_image') if request else None
        size_ids = request.data.getlist('size_id') if request else []

        # Create product with thumbnail image if provided
        if thumbnail_image:
            validated_data['thumbnail_image'] = thumbnail_image

        # Remove size from validated_data as we'll handle it separately
        validated_data.pop('size', None)

        # Create the product
        product = Product.objects.create(**validated_data)

        # Handle sizes
        if size_ids:
            product.size.set(size_ids)

        # Create product images
        index = 0
        while True:
            image_file = request.FILES.get(f'image_data[{index}][image]')
            if not image_file:
                break

            color = request.data.get(f'image_data[{index}][color]')
            stock = request.data.get(f'image_data[{index}][image_stock]')
            ProductImage.objects.create(
                product=product,
                image=image_file,
                image_alt_description=image_file.name,
                color=color,
                stock=stock
            )
            index += 1

        return product

    def update(self, instance, validated_data):
        request = self.context.get('request')
        thumbnail_image = request.FILES.get(
            'thumbnail_image') if request else None
        size_ids = request.data.getlist('size_id') if request else []

        # Update thumbnail image if provided
        if thumbnail_image:
            if instance.thumbnail_image:
                instance.thumbnail_image.delete()
            instance.thumbnail_image = thumbnail_image

        # Remove size from validated_data as we'll handle it separately
        validated_data.pop('size', None)

        # Update basic product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update sizes
        if size_ids:
            instance.size.set(size_ids)

        # Update or add images
        index = 0
        while True:
            image_file = request.FILES.get(f'image_data[{index}][image]')
            image_id = request.data.get(f'image_data[{index}][id]')
            color = request.data.get(f'image_data[{index}][color]')
            stock = request.data.get(f'image_data[{index}][image_stock]')
            if not image_file and not image_id:
                break

            if image_id:
                # Update existing image
                try:
                    product_image = ProductImage.objects.get(
                        id=image_id, product=instance)
                    if image_file:
                        product_image.image.delete()
                        product_image.image = image_file
                        product_image.image_alt_description = image_file.name
                    if color is not None:
                        product_image.color = color
                    if stock is not None:
                        product_image.stock = stock
                    product_image.save()
                except ProductImage.DoesNotExist:
                    pass  # Optionally handle this case
            elif image_file:
                # Add new image
                ProductImage.objects.create(
                    product=instance,
                    image=image_file,
                    image_alt_description=image_file.name,
                    color=color,
                    stock=stock
                )
            index += 1

        return instance


class ProductReviewSmallSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'review',
                  'rating', 'created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    size = SizeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    thumbnail_image = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    subsubcategory = SubSubCategorySerializer(read_only=True)
    reviews = ProductReviewSmallSerializer(
        many=True, read_only=True, source='productreview_set')
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_thumbnail_image(self, obj):
        if obj.thumbnail_image:
            return f'/media/{obj.thumbnail_image.name}'
        return None

    def get_reviews_count(self, obj):
        return ProductReview.objects.only('id').filter(product=obj).count()

    def get_average_rating(self, obj):
        return ProductReview.objects.only('id').filter(product=obj).aggregate(
            avg_rating=Avg('rating'))['avg_rating'] or 0


class ProductSmallSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    subsubcategory = SubSubCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'market_price',
                  'price', 'thumbnail_image', 'meta_title', 'meta_description', 'category', 'subcategory', 'subsubcategory']


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


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    subcategory = SubCategoryListSerializer(read_only=True)
    subsubcategory = SubSubCategoryListSerializer(read_only=True)
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'market_price', 'thumbnail_image', 'thumbnail_image_alt_description', 'stock',
            'reviews_count', 'average_rating', 'category', 'subcategory', 'subsubcategory', 'is_featured', 'is_popular', 'is_active'
        ]

    def get_reviews_count(self, obj):
        return ProductReview.objects.only('id').filter(product=obj).count()

    def get_average_rating(self, obj):
        return ProductReview.objects.only('id').filter(product=obj).aggregate(
            avg_rating=Avg('rating'))['avg_rating'] or 0


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
                  'rating', 'created_at']


class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()
