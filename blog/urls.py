from django.urls import path
from . import views

urlpatterns = [
    # Blog Category URLs
    path('blog/categories/', views.BlogCategoryListCreateView.as_view(),
         name='category-list-create'),
    path('blog/categories/<slug:slug>/', views.BlogCategoryRetrieveUpdateDestroyView.as_view(),
         name='category-retrieve-update-destroy'),

    # Blog Tag URLs
    path('blog/tags/', views.BlogTagListCreateView.as_view(), name='tag-list-create'),
    path('blog/tags/<int:pk>/', views.BlogTagRetrieveUpdateDestroyView.as_view(),
         name='tag-retrieve-update-destroy'),

    # Blog URLs
    path('blogs/', views.BlogListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<slug:slug>/', views.BlogRetrieveUpdateDestroyView.as_view(),
         name='blog-retrieve-update-destroy'),
    path('blogs/<slug:slug>/similar/', views.SimilarBlogListView.as_view(),
         name='similar-blog-list'),

    # Blog Comment URLs
    path('blog/comments/', views.BlogCommentListCreateView.as_view(),
         name='blog-comment-list-create'),
    path('blog/comments/<int:id>/', views.BlogCommentRetrieveUpdateDestroyView.as_view(),
         name='blog-comment-retrieve-update-destroy'),

    # Testimonial URLs
    path('testimonials/', views.TestimonialListCreateView.as_view(),
         name='testimonial-list-create'),
    path('testimonials/<int:id>/', views.TestimonialRetrieveUpdateDestroyView.as_view(),
         name='testimonial-retrieve-update-destroy'),
]
