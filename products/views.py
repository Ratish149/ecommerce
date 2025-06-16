import requests
import os
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils.text import slugify
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import pandas as pd
import io
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl import Workbook
from django.http import HttpResponse
from rest_framework import generics
from .models import Product, ProductCategory, ProductSubCategory, Wishlist, ProductReview, ProductImage, Size
from .serializers import ProductSerializer, CategorySerializer, SubCategorySerializer, ProductDetailSerializer, WishlistSerializer, ProductReviewDetailSerializer, ProductReviewSerializer, ProductImageSerializer, ProductImageSmallSerializer, BulkProductUploadSerializer, SizeSerializer
from django_filters import rest_framework as django_filters
from rest_framework import filters
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# Create your views here.


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductSubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            return ProductSubCategory.objects.filter(category__slug=category_slug)
        return ProductSubCategory.objects.all()


class SubCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductSubCategory.objects.all()
    serializer_class = SubCategorySerializer
    lookup_field = 'slug'


class SizeListCreateView(generics.ListCreateAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class SizeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    lookup_field = 'id'


class ProductImageListCreateView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSmallSerializer


class ProductImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    lookup_field = 'id'

    def get_object(self):
        try:
            return ProductImage.objects.get(id=self.kwargs['id'])
        except ProductImage.DoesNotExist:
            raise Http404("Product image not found")

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductImageSmallSerializer
        return ProductImageSerializer


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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
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


class ProductReviewFilter(django_filters.FilterSet):
    rating = django_filters.NumberFilter(
        field_name='rating', lookup_expr='exact')

    class Meta:
        model = ProductReview
        fields = ['rating']


class ProductReviewView(generics.ListCreateAPIView):
    queryset = ProductReview.objects.all().order_by('-created_at')
    serializer_class = ProductReviewSerializer
    filter_backends = [django_filters.DjangoFilterBackend,]
    filterset_class = ProductReviewFilter

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


class ProductReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    lookup_field = 'id'


class BulkProductUploadView(APIView):
    serializer_class = BulkProductUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = BulkProductUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = serializer.process_file()
                # Pass request context to ProductSerializer
                product_serializer = ProductSerializer(
                    result['products'],
                    many=True,
                    context={'request': request}
                )
                return Response({
                    'message': f'Successfully uploaded {result["success"]} products',
                    'errors': result['errors'] if result['errors'] else None,
                    'products': product_serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductExcelExportWithDropdownAPIView(APIView):
    def get(self, request, format=None):
        # Get all products and categories
        product = Product.objects.select_related(
            'category', 'subcategory').all().first()
        categories = list(
            ProductCategory.objects.all().values_list('name', flat=True))
        sub_categories = list(
            ProductSubCategory.objects.all().values_list('name', flat=True))
        sizes = list(Size.objects.all().values_list('name', flat=True))

        # Prepare data for Excel
        data = []
        data.append({
            'Product Name': "Product Name",
            'Category': product.category.name if product.category else 'Category',
            'Sub Category': product.subcategory.name if product.subcategory else 'Sub Category',
            'Price': "999.00",
            'Market Price': "599.00",
            'Discount': '10',
            'Stock': '100',
            'Is popular': 'true' if product.is_popular else 'false',
            'Is featured': 'true' if product.is_featured else 'false',
            'Meta Title': 'Meta Title',
            'Meta Description': 'Meta Description',
            'Size': 'size1, size2',  # Example showing multiple sizes
            'Thumbnail image': 'thumbnail_image_url',
            'Thumbnail Image Alt Description': 'thumbnail_image_alt_description',
            'Images': 'image1_url, image2_url',  # Example showing multiple images
            'Description': 'Product description',
        })

        # Create Excel file with dropdown
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Products"

        # Write headers
        headers = [
            'Product Name', 'Category', 'Sub Category', 'Price', 'Market Price', 'Discount',
            'Stock', 'Is popular', 'Is featured', 'Meta Title', 'Meta Description',
            'Size', 'Thumbnail image', 'Thumbnail Image Alt Description', 'Images', 'Description'
        ]
        ws.append(headers)

        # Write product data
        for item in data:
            ws.append([item[header] for header in headers])

        # Add dropdown validation for Category column
        dv = DataValidation(
            type="list",
            formula1=f'"{",".join(categories)}"',
            allow_blank=True
        )
        dv.add(f'B2:B{len(data)+1}')
        ws.add_data_validation(dv)

        # Add dropdown validation for Sub Category column
        dv = DataValidation(
            type="list",
            formula1=f'"{",".join(sub_categories)}"',
            allow_blank=True
        )
        dv.add(f'C2:C{len(data)+1}')
        ws.add_data_validation(dv)

        # Add dropdown validation for boolean fields
        for col in ['H', 'I']:
            dv = DataValidation(
                type="list",
                formula1='"true,false"',
                allow_blank=True
            )
            dv.add(f'{col}2:{col}{len(data)+1}')
            ws.add_data_validation(dv)
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_cells = [cell for cell in column]
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column_cells[0].column_letter].width = adjusted_width

        # Save to BytesIO
        wb.save(output)

        # Prepare HTTP response
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="products_export.xlsx"'
        return response


class UploadProductExcelView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        df = pd.read_excel(excel_file)

        for _, row in df.iterrows():
            try:
                # Get or create category and subcategory
                category, _ = ProductCategory.objects.get_or_create(
                    name=row['Category'])
                subcategory, _ = ProductSubCategory.objects.get_or_create(
                    name=row['Sub Category'], category=category
                )

                # Create Product instance
                product = Product(
                    name=row['Product Name'],
                    description=row.get('Description', ''),
                    price=row['Price'],
                    market_price=row['Market Price'],
                    stock=row['Stock'],
                    is_popular=row['Is popular'],
                    is_featured=row['Is featured'],
                    discount=row.get('Discount') or 0.0,
                    meta_title=row.get('Meta Title', ''),
                    meta_description=row.get('Meta Description', ''),
                    category=category,
                    subcategory=subcategory,
                )

                # Download and attach thumbnail image
                thumb_url = row.get('Thumbnail image')
                if thumb_url:
                    thumb_response = requests.get(thumb_url, stream=True)
                    if thumb_response.status_code == 200:
                        thumb_temp = NamedTemporaryFile(delete=True)
                        for chunk in thumb_response.iter_content(1024):
                            thumb_temp.write(chunk)
                        thumb_temp.flush()
                        file_ext = os.path.splitext(thumb_url)[-1][:5]
                        product.thumbnail_image.save(
                            f"thumb_{slugify(product.name)}{file_ext}", File(thumb_temp))

                # Save product to DB
                product.save()

                # Handle sizes
                sizes = row.get('Size', '')
                for size_name in sizes.split(','):
                    size_name = size_name.strip()
                    if size_name:
                        size_obj, _ = Size.objects.get_or_create(
                            name=size_name)
                        product.size.add(size_obj)

                # Handle product images
                image_urls = row.get('Images', '').split(',')
                for image_url in image_urls:
                    image_url = image_url.strip()
                    if image_url:
                        img_response = requests.get(image_url, stream=True)
                        if img_response.status_code == 200:
                            img_temp = NamedTemporaryFile(delete=True)
                            for chunk in img_response.iter_content(1024):
                                img_temp.write(chunk)
                            img_temp.flush()
                            ext = os.path.splitext(image_url)[-1][:5]
                            ProductImage.objects.create(
                                product=product,
                                image=File(
                                    img_temp, name=f"img_{slugify(product.name)}{ext}"),
                                name=f"img_{slugify(product.name)}"
                            )

            except Exception as e:
                return Response({"error": str(e), "product": row.get('Product Name')}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Products created successfully."})
