from rest_framework import serializers
from .models import Product, ProductCategory, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return f'/media/{obj.image.name}'
        return None


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
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

    def get_thumbnail_image(self, obj):
        if obj.thumbnail_image:
            return f'/media/{obj.thumbnail_image.name}'
        return None

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


class ProductDetailSerializer(serializers.ModelSerializer):

    images = ProductImageSerializer(many=True, read_only=True)
    thumbnail_image = serializers.SerializerMethodField()
    category=CategorySerializer()


    class Meta:
        model = Product
        fields = '__all__'

    def get_thumbnail_image(self, obj):
        if obj.thumbnail_image:
            return f'/media/{obj.thumbnail_image.name}'
        return None


class ProductSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'market_price',
                  'price', 'thumbnail_image', 'meta_title', 'meta_description','category_slug']