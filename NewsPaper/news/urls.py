from django.urls import path
from .views import (PostListView, PostDeleteView,
                    PostUpdateView, PostCreateView, PostDetailView, NewsSearchView, BecomeAuthorView,
                    SubscribeToCategoryView, UnsubscribeFromCategoryView)


urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),

    path('posts/search/', NewsSearchView.as_view(), name='search'),

    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),

    path('news/create/', PostCreateView.as_view(), name='news_create'),
    path('articles/create/', PostCreateView.as_view(), name='article_create'),

    path('news/<int:pk>/edit/', PostUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', PostUpdateView.as_view(), name='article_edit'),

    path('news/<int:pk>/delete/', PostDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', PostDeleteView.as_view(), name='article_delete'),

    path('become_author/', BecomeAuthorView.as_view(), name='become_author'),

    path('subscribe/<int:category_id>/<int:post_id>/', SubscribeToCategoryView.as_view(),
         name='subscribe_to_category'),
    path('unsubscribe/<int:category_id>/<int:post_id>/', UnsubscribeFromCategoryView.as_view(),
         name='unsubscribe_from_category'),
]
