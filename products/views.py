import csv
from .serializers import ImportSerializer
from .models import Product, ProductCategory, ProductSubCategory, Size, ProductImage
import openpyxl
from rest_framework.parsers import MultiPartParser
from django.core.files.base import ContentFile
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
from .serializers import ProductSerializer, CategorySerializer, SubCategorySerializer, ProductDetailSerializer, WishlistSerializer, ProductReviewDetailSerializer, ProductReviewSerializer, ProductImageSerializer, ProductImageSmallSerializer, SizeSerializer, ImportSerializer, ProductListSerializer, CategorySmallSerializer, SubCategorySmallSerializer
from django_filters import rest_framework as django_filters
from rest_framework import filters
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
# Create your views here.


class CustomPagination(PageNumberPagination):
    page_size = 18
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.only(
        'id', 'name', 'slug', 'description', 'image')
    serializer_class = CategorySerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategorySmallSerializer
        return CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.only(
        'id', 'name', 'slug', 'description', 'image')
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategorySmallSerializer
        return CategorySerializer


class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductSubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubCategorySmallSerializer
        return SubCategorySerializer

    def get_queryset(self):
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            return ProductSubCategory.objects.filter(category__slug=category_slug).only('id', 'name', 'slug', 'category', 'image').select_related('category')
        return ProductSubCategory.objects.all()


class SubCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductSubCategory.objects.only(
        'id', 'name', 'slug', 'category', 'image').select_related('category')
    serializer_class = SubCategorySerializer
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubCategorySmallSerializer
        return SubCategorySerializer


class SizeListCreateView(generics.ListCreateAPIView):
    queryset = Size.objects.only('id', 'name', 'description', 'image')
    serializer_class = SizeSerializer


class SizeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Size.objects.only('id', 'name', 'description', 'image')
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
    subcategory = django_filters.CharFilter(
        field_name='subcategory__slug', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(
        field_name='is_popular', lookup_expr='exact')
    is_featured = django_filters.BooleanFilter(
        field_name='is_featured', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['name', 'min_price', 'max_price', 'category',
                  'subcategory', 'is_popular', 'is_featured']


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.only(
        'id', 'name', 'slug', 'market_price', 'price', 'is_popular', 'is_featured',
        'thumbnail_image', 'thumbnail_image_alt_description'
    ).order_by('-created_at')
    serializer_class = ProductSerializer
    filter_backends = [django_filters.DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'price', '-name', '-price', '-created_at']
    filterset_class = ProductFilter
    pagination_class = CustomPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer


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
    serializer_class = ProductListSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        try:
            product = Product.objects.only('id', 'category').get(slug=slug)
            # Get products from the same category, excluding the current product
            similar_products = Product.objects.only(
                'id', 'name', 'slug', 'market_price', 'price', 'is_popular', 'is_featured',
                'thumbnail_image', 'thumbnail_image_alt_description'
            ).filter(
                category=product.category,
                is_active=True
            ).exclude(
                id=product.id
            ).order_by('-created_at')[:3]
            return similar_products
        except Product.DoesNotExist:
            return Product.objects.none()


class WishlistListCreateView(generics.ListCreateAPIView):
    queryset = Wishlist.objects.only(
        'id', 'user', 'product', 'created_at', 'updated_at'
    ).select_related(
        'user',
        'product'
    )
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wishlist.objects.only(
        'id', 'user', 'product', 'created_at', 'updated_at'
    ).select_related(
        'user',
        'product'
    )
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
    queryset = ProductReview.objects.only(
        'id', 'product', 'user', 'review', 'rating', 'created_at', 'updated_at'
    ).select_related('product', 'user').order_by('-created_at')
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
            product = Product.objects.only('id').get(slug=slug)
            return ProductReview.objects.filter(product=product)
        except Product.DoesNotExist:
            return ProductReview.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductReview.objects.only(
        'id', 'product', 'user', 'review', 'rating', 'created_at', 'updated_at'
    ).select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    lookup_field = 'id'


class ProductExcelExportWithDropdownAPIView(APIView):
    def get(self, request, format=None):
        categories = list(
            ProductCategory.objects.values_list('name', flat=True))
        sub_categories = list(
            ProductSubCategory.objects.values_list('name', flat=True))
        sizes = list(Size.objects.values_list('name', flat=True))

        # Setup workbook
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Products"

        # Define headers
        headers = [
            'Product Name', 'Category', 'Sub Category', 'Price', 'Market Price', 'Discount',
            'Product Stock', 'Is popular', 'Is featured', 'Description', 'Meta Title', 'Meta Description',
            'Size', 'Thumbnail image', 'Thumbnail Image Alt Description',
            'Color', 'Stock (Color)', 'Images', 'Image Alt Description'
        ]
        ws.append(headers)

        # Sample common data (only on first row)
        common_data = {
            'Product Name': 'Product Name',
            'Category': 'Category',
            'Sub Category': 'Sub Category',
            'Price': 100,
            'Market Price': 100,
            'Discount': 100,
            'Product Stock': 100,
            'Is popular': 'TRUE',
            'Is featured': 'FALSE',
            'Description': 'Product Description',
            'Meta Title': 'Product Meta Title',
            'Meta Description': 'Product Meta Description',
            'Size': 'S, M, L',
            'Thumbnail image': 'https://example.com/thumbnail.jpg',
            'Thumbnail Image Alt Description': 'Thumbnail Alt Description',
        }

        # Sample image rows with 3 variants (Color 1, 2, 3)
        for i in range(3):
            row = []
            for h in headers:
                if h in ['Color', 'Stock (Color)', 'Images', 'Image Alt Description']:
                    continue
                # Fill only on first row
                row.append(common_data[h] if i == 0 else '')

            row.append(f'Color {i+1}')
            row.append(10 * (i+1))  # Stock
            row.append(f'https://example.com/image{i+1}.jpg')
            row.append(f'Image Alt Description {i+1}')

            ws.append(row)

        # Dropdowns for category and subcategory
        if categories:
            dv = DataValidation(
                type="list", formula1=f'"{",".join(categories)}"', allow_blank=True)
            dv.add("B2:B100")
            ws.add_data_validation(dv)

        if sub_categories:
            dv = DataValidation(
                type="list", formula1=f'"{",".join(sub_categories)}"', allow_blank=True)
            dv.add("C2:C100")
            ws.add_data_validation(dv)

        # Dropdown for booleans
        for col in ['H', 'I']:
            dv = DataValidation(
                type="list", formula1='"TRUE,FALSE"', allow_blank=True)
            dv.add(f"{col}2:{col}100")
            ws.add_data_validation(dv)

        # Auto column width
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_len + 2

        # Return Excel file
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
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


class ProductExcelImportAPIView(APIView):
    serializer_class = ImportSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        file_name = file.name.lower()
        try:
            if file_name.endswith('.csv'):
                rows = self.read_csv(file)

            elif file_name.endswith(('.xlsx', '.xls')):
                rows = self.read_excel(file)
            else:
                return Response({'error': 'Unsupported file type. Use CSV or Excel.'}, status=400)

            return self.process_rows(rows)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def read_csv(self, file):
        decoded_file = file.read().decode('utf-8-sig')  # ✅ decode with BOM-aware codec
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        cleaned_rows = []

        for row in reader:
            cleaned_row = {key.strip(): (value.strip() if isinstance(value, str) else value)
                           for key, value in row.items()}
            cleaned_rows.append(cleaned_row)

        return cleaned_rows

    def read_excel(self, file):
        wb = openpyxl.load_workbook(file)
        ws = wb.active
        header = [cell.value for cell in ws[1]]
        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            row_data = dict(zip(header, row))
            rows.append(row_data)
        return rows

    def process_rows(self, rows):
        last_product = None
        for row_data in rows:
            name = row_data.get('Product Name')

            if name:
                category_name = str(row_data.get('Category') or '').strip()
                category, _ = ProductCategory.objects.get_or_create(
                    name=category_name)

                subcategory_name = str(row_data.get(
                    'Sub Category') or '').strip()
                subcategory, _ = ProductSubCategory.objects.get_or_create(
                    name=subcategory_name,
                    category=category
                )

                product = Product.objects.create(
                    name=name,
                    slug=slugify(name),
                    price=row_data.get('Price') or 0,
                    market_price=row_data.get('Market Price') or 0,
                    discount=row_data.get('Discount') or 0,
                    stock=row_data.get('Product Stock') or 0,
                    is_popular=(
                        str(row_data.get('Is popular')).lower() == 'true'),
                    is_featured=(
                        str(row_data.get('Is featured')).lower() == 'true'),
                    description=row_data.get('Description') or '',
                    meta_title=row_data.get('Meta Title') or '',
                    meta_description=row_data.get('Meta Description') or '',
                    thumbnail_image_alt_description=row_data.get(
                        'Thumbnail Image Alt Description') or '',
                    category=category,
                    subcategory=subcategory
                )

                sizes = [s.strip() for s in str(row_data.get(
                    'Size') or '').split(',') if s.strip()]
                for size_name in sizes:
                    size_obj, _ = Size.objects.get_or_create(name=size_name)
                    product.size.add(size_obj)

                thumbnail_url = row_data.get('Thumbnail image')
                if thumbnail_url:
                    try:
                        response = requests.get(thumbnail_url)
                        if response.status_code == 200:
                            filename = thumbnail_url.split(
                                "/")[-1].split("?")[0] or f"{slugify(name)}-thumb.jpg"
                            product.thumbnail_image.save(
                                filename, ContentFile(response.content), save=True)
                    except Exception as e:
                        print(f"[Thumbnail] Failed for {name}: {e}")

                last_product = product

            product = last_product
            if not product:
                continue

            img_url = row_data.get('Images')
            if img_url:
                try:
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        image_file = ContentFile(response.content)
                        image_filename = img_url.split(
                            "/")[-1].split("?")[0] or f"{slugify(product.name)}.jpg"
                        image_instance = ProductImage.objects.create(
                            product=product,
                            color=row_data.get('Color') or '',
                            stock=row_data.get('Stock (Color)') or 0,
                            image_alt_description=row_data.get(
                                'Image Alt Description') or '',
                        )
                        image_instance.image.save(
                            image_filename, image_file, save=True)
                except Exception as e:
                    print(f"[Image] Failed for {product.name}: {e}")

        return Response({'message': 'Products imported successfully'}, status=201)
