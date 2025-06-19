from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import BlogCategory, BlogComment, BlogTag, Blog, Testimonial
from .serializers import BlogCategorySerializer, BlogCommentSerializer, BlogSmallSerializer, BlogTagSerializer, BlogSerializer, TestimonialSerializer
from django_filters import rest_framework as django_filters
from rest_framework import filters

# Create your views here.


class BlogCategoryListCreateView(generics.ListCreateAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer


class BlogCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    lookup_field = 'slug'


class BlogTagListCreateView(generics.ListCreateAPIView):
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer


class BlogTagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer


class CustomPagination(PageNumberPagination):
    page_size = 10
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
        'id', 'title', 'slug', 'thumbnail_image', 'thumbnail_image_alt_description',
        'meta_title', 'meta_description', 'created_at', 'updated_at',
        'category', 'author', 'author__first_name', 'author__last_name', 'author__username', 'author__email', 'author__id',
        'category__title', 'category__slug', 'category__id',
    ).select_related('category', 'author').prefetch_related('tags')
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
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'


class BlogCommentListCreateView(generics.ListCreateAPIView):
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer


class BlogCommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer
    lookup_field = 'id'


class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer


class TestimonialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    lookup_field = 'id'
