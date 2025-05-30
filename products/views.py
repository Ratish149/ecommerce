from rest_framework import generics
from .models import Product, ProductCategory
from .serializers import ProductSerializer, CategorySerializer, ProductDetailSerializer
from django_filters import rest_framework as django_filters
from rest_framework import filters
# Create your views here.


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(
        field_name='is_popular', lookup_expr='exact')
    is_featured = django_filters.BooleanFilter(
        field_name='is_featured', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['name', 'min_price', 'max_price', 'category',
                  'is_popular', 'is_featured']


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filter_backends = [django_filters.DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'price', '-name', '-price', '-created_at']
    filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class SimilarProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        try:
            product = Product.objects.get(slug=slug)
            # Get products from the same category, excluding the current product
            similar_products = Product.objects.filter(
                category=product.category,
                is_active=True
            ).exclude(
                id=product.id
            ).order_by('-created_at')[:3]  # Limit to 6 similar products
            return similar_products
        except Product.DoesNotExist:
            return Product.objects.none()
