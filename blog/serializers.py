from rest_framework import serializers
from .models import BlogCategory, BlogComment, BlogTag, Blog


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'slug', 'created_at', 'updated_at']


class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'title', 'created_at', 'updated_at']


class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['id', 'blog', 'user', 'comment', 'created_at', 'updated_at']


class BlogSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    comments = BlogCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'description', 'meta_title',
            'meta_description', 'thumbnail_image', 'thumbnail_image_alt_description',
            'category', 'tags', 'comments', 'created_at', 'updated_at'
        ]


class BlogSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'thumbnail_image', 'thumbnail_image_alt_description',
                  'meta_title', 'meta_description', 'created_at', 'updated_at']
