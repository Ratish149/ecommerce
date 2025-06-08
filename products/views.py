from rest_framework import generics
from .models import Product, ProductCategory, Wishlist, ProductReview, ProductImage
from .serializers import ProductSerializer, CategorySerializer, ProductDetailSerializer, WishlistSerializer, ProductReviewDetailSerializer, ProductReviewSerializer, ProductImageSerializer
from django_filters import rest_framework as django_filters
from rest_framework import filters
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class ProductImageListCreateView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class ProductImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

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

    def get_object(self):
        category_slug = self.kwargs.get('category_slug')
        slug = self.kwargs.get('slug')

        try:
            return Product.objects.get(category__slug=category_slug, slug=slug)
        except Product.DoesNotExist:
            raise Http404("Product not found")
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductDetailSerializer
        return ProductSerializer


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


class WishlistListCreateView(generics.ListCreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_object(self):
        try:
            return Wishlist.objects.get(user=self.request.user)
        except Wishlist.DoesNotExist:
            raise Http404("Wishlist not found")

    def delete(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('id')
            wishlist = Wishlist.objects.get(
                user=self.request.user, id=id)
            wishlist.delete()
            return Response({"message": "Product removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)
        except Wishlist.DoesNotExist:
            raise Http404("Wishlist not found")


class ProductReviewView(generics.ListCreateAPIView):
    queryset = ProductReview.objects.all().order_by('-created_at')
    serializer_class = ProductReviewSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductReviewDetailSerializer
        return ProductReviewSerializer

    def get_queryset(self):
        slug = self.request.query_params.get('slug')
        try:
            product = Product.objects.get(slug=slug)
            return ProductReview.objects.filter(product=product)
        except Product.DoesNotExist:
            return ProductReview.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
