from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import BlogCategory, BlogComment, BlogTag, Blog, Testimonial
from .serializers import BlogCategorySerializer, BlogCommentSerializer, BlogCommentSmallSerializer, BlogSmallSerializer, BlogTagSerializer, BlogSerializer, TestimonialSerializer
from django_filters import rest_framework as django_filters
from rest_framework import filters
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.response import Response

# Create your views here.


class BlogCategoryListCreateView(generics.ListCreateAPIView):
    queryset = BlogCategory.objects.only(
        'id', 'title', 'slug', 'created_at', 'updated_at')
    serializer_class = BlogCategorySerializer


class BlogCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogCategory.objects.only(
        'id', 'title', 'slug', 'created_at', 'updated_at')
    serializer_class = BlogCategorySerializer
    lookup_field = 'slug'


class BlogTagListCreateView(generics.ListCreateAPIView):
    queryset = BlogTag.objects.only(
        'id', 'title', 'created_at', 'updated_at')
    serializer_class = BlogTagSerializer


class BlogTagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogTag.objects.only(
        'id', 'title', 'created_at', 'updated_at')
    serializer_class = BlogTagSerializer


class CustomPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class BlogFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=BlogCategory.objects.all(),
        label='Category',
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=BlogTag.objects.all(),
        label='Tags',
    )

    class Meta:
        model = Blog
        fields = ['category', 'tags']


class BlogListCreateView(generics.ListCreateAPIView):
    queryset = Blog.objects.only(
        'id', 'title', 'slug', 'thumbnail_image', 'thumbnail_image_alt_description', 'created_at', 'updated_at',
        'category', 'category__title', 'category__slug'
    ).select_related('category').prefetch_related('tags')
    serializer_class = BlogSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter,
                       django_filters.DjangoFilterBackend]
    search_fields = ['title']
    filterset_class = BlogFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BlogSmallSerializer
        return BlogSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            serializer.save()


class BlogRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.only(
        'id', 'title', 'slug', 'thumbnail_image', 'thumbnail_image_alt_description', 'created_at', 'updated_at',
        'category', 'category__title', 'category__slug'
    ).select_related('category').prefetch_related('tags')
    serializer_class = BlogSerializer
    lookup_field = 'slug'


class SimilarBlogListView(APIView):
    def get(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        # Get blogs with the same category or overlapping tags, excluding the current blog
        similar_blogs = Blog.objects.filter(
            models.Q(category=blog.category) |
            models.Q(tags__in=blog.tags.all())
        ).exclude(id=blog.id).distinct()[:4]

        serializer = BlogSmallSerializer(similar_blogs, many=True)
        return Response(serializer.data)


class BlogCommentListCreateView(generics.ListCreateAPIView):
    queryset = BlogComment.objects.only(
        'id', 'blog', 'user', 'comment', 'created_at', 'updated_at')
    serializer_class = BlogCommentSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BlogCommentSmallSerializer
        return BlogCommentSerializer


class BlogCommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogComment.objects.only(
        'id', 'blog', 'user', 'comment', 'created_at', 'updated_at')
    serializer_class = BlogCommentSerializer
    lookup_field = 'id'


class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.only(
        'id', 'name', 'designation', 'image', 'comment', 'created_at', 'updated_at')
    serializer_class = TestimonialSerializer


class TestimonialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.only(
        'id', 'name', 'designation', 'image', 'comment', 'created_at', 'updated_at')
    serializer_class = TestimonialSerializer
    lookup_field = 'id'
