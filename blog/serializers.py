from rest_framework import serializers
from .models import BlogCategory, BlogComment, BlogTag, Blog, Testimonial
from accounts.serializers import UserSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'slug', 'created_at', 'updated_at']


class BlogCategorySmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'slug']


class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'title', 'created_at', 'updated_at']


class BlogTagSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'title']


class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['id', 'blog', 'user', 'comment', 'created_at', 'updated_at']


class BlogCommentSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['id', 'blog', 'user', 'comment', 'created_at']


class BlogSerializer(serializers.ModelSerializer):
    category = BlogCategorySmallSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BlogCategory.objects.all(),
        write_only=True,
        source='category'
    )
    tags = BlogTagSmallSerializer(many=True, read_only=True)
    tags_id = serializers.PrimaryKeyRelatedField(
        queryset=BlogTag.objects.all(),
        write_only=True,
        source='tags',
        many=True
    )
    comments = BlogCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'author', 'title', 'slug', 'description', 'meta_title',
            'meta_description', 'thumbnail_image', 'thumbnail_image_alt_description',
            'category', 'category_id', 'tags', 'tags_id', 'comments', 'created_at', 'updated_at'
        ]


class BlogSmallSerializer(serializers.ModelSerializer):
    category = BlogCategorySmallSerializer(read_only=True)
    tags = BlogTagSmallSerializer(many=True, read_only=True)
    thumbnail_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'thumbnail_image', 'thumbnail_image_alt_description',
                  'category', 'tags', 'created_at', 'updated_at']

    def get_thumbnail_image(self, obj):
        if obj.thumbnail_image:
            return f'/media/{obj.thumbnail_image.name}'
        return None


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'designation', 'image',
                  'comment', 'created_at', 'updated_at']
