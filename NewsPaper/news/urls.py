from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(60*10)(views.PostListView.as_view()), name='post_list'),

    path('posts/search/', views.NewsSearchView.as_view(), name='search'),

    path('posts/<int:pk>/', cache_page(60*10)(views.PostDetailView.as_view()), name='post_detail'),

    path('news/create/', views.PostCreateView.as_view(), name='news_create'),
    path('articles/create/', views.PostCreateView.as_view(), name='article_create'),

    path('news/<int:pk>/edit/', views.PostUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', views.PostUpdateView.as_view(), name='article_edit'),

    path('news/<int:pk>/delete/', views.PostDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', views.PostDeleteView.as_view(), name='article_delete'),

    path('become_author/', views.BecomeAuthorView.as_view(), name='become_author'),

    path('subscribe/<int:category_id>/<int:post_id>/', views.SubscribeToCategoryView.as_view(),
         name='subscribe_to_category'),
    path('unsubscribe/<int:category_id>/<int:post_id>/', views.UnsubscribeFromCategoryView.as_view(),
         name='unsubscribe_from_category'),
]
