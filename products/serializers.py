from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Product, ProductCategory, ProductImage, Wishlist, ProductReview, ProductSubCategory, Size, Color
import pandas as pd


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductSubCategory
        fields = '__all__'

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
        fields = ['id', 'image', 'image_alt_description', 'color', 'product']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request and request.method == 'GET':
                return f'/media/{obj.image.name}'
            return obj.image.url
        return None


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_alt_description',
                  'color', 'product', 'product_name']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request and request.method == 'GET':
                return f'/media/{obj.image.name}'
            return obj.image.url
        return None


class ProductSerializer(serializers.ModelSerializer):
    size = SizeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
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
            ProductImage.objects.create(
                product=product,
                image=image_file,
                image_alt_description=image_file.name,
                color=color
            )
            index += 1

        return product

    def update(self, instance, validated_data):
        request = self.context.get('request')
        thumbnail_image = request.FILES.get(
            'thumbnail_image') if request else None
        size_ids = request.data.getlist('size_id') if request else []
        delete_images = request.data.getlist(
            'delete_images') if request else []

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

        # Delete specified images
        if delete_images:
            ProductImage.objects.filter(
                id__in=delete_images, product=instance).delete()

        # Add new images
        index = 0
        while True:
            image_file = request.FILES.get(f'image_data[{index}][image]')
            if not image_file:
                break

            color = request.data.get(f'image_data[{index}][color]')
            ProductImage.objects.create(
                product=instance,
                image=image_file,
                image_alt_description=image_file.name,
                color=color
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
    reviews = ProductReviewSmallSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_thumbnail_image(self, obj):
        if obj.thumbnail_image:
            return f'/media/{obj.thumbnail_image.name}'
        return None


class ProductSmallSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'market_price',
                  'price', 'thumbnail_image', 'meta_title', 'meta_description', 'category', 'subcategory', 'reviews']


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


class BulkProductUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    file_type = serializers.ChoiceField(choices=['csv', 'excel'])

    def validate_file(self, value):
        if value.name.endswith('.csv') or value.name.endswith('.xlsx') or value.name.endswith('.xls'):
            return value
        raise serializers.ValidationError("File must be CSV or Excel format")

    def process_file(self):
        file = self.validated_data['file']
        file_type = self.validated_data['file_type']

        if file_type == 'csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        required_columns = ['name', 'description', 'market_price',
                            'price', 'stock', 'category', 'subcategory']
        missing_columns = [
            col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise serializers.ValidationError(
                f"Missing required columns: {', '.join(missing_columns)}")

        products = []
        errors = []

        for index, row in df.iterrows():
            try:
                # Get or create category
                category, _ = ProductCategory.objects.get_or_create(
                    name=row['category'],
                    defaults={'description': row.get(
                        'category_description', '')}
                )

                # Get or create subcategory
                subcategory, _ = ProductSubCategory.objects.get_or_create(
                    name=row['subcategory'],
                    category=category,
                    defaults={'description': row.get(
                        'subcategory_description', '')}
                )

                # Create product
                product_data = {
                    'name': row['name'],
                    'description': row['description'],
                    'market_price': float(row['market_price']),
                    'price': float(row['price']),
                    'stock': int(row['stock']),
                    'category': category,
                    'subcategory': subcategory,
                    'is_popular': row.get('is_popular', False),
                    'is_featured': row.get('is_featured', False),
                    'discount': float(row.get('discount', 0)),
                    'is_active': row.get('is_active', True),
                    'meta_title': row.get('meta_title', ''),
                    'meta_description': row.get('meta_description', '')
                }

                # Create the product first
                product = Product.objects.create(**product_data)

                # Handle sizes if provided
                if 'sizes' in row and pd.notna(row['sizes']):
                    sizes = [s.strip() for s in str(row['sizes']).split(',')]
                    size_objects = [Size.objects.get_or_create(name=s)[
                        0] for s in sizes]
                    product.size.set(size_objects)

                products.append(product)

            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")

        return {
            'success': len(products),
            'errors': errors,
            'products': products
        }
