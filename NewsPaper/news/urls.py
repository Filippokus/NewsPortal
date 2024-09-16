from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (PostListView, PostDeleteView,
                    PostUpdateView, PostCreateView, PostDetailView, NewsSearchView)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('posts/search/', NewsSearchView.as_view(), name='search'),


    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),

    path('news/create/', PostCreateView.as_view(), name='news_create'),
    path('articles/create/', PostCreateView.as_view(), name='article_create'),

    path('news/<int:pk>/edit/', PostUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', PostUpdateView.as_view(), name='article_edit'),

    path('news/<int:pk>/delete/', PostDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', PostDeleteView.as_view(), name='article_delete'),
]