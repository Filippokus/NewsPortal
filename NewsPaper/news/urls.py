from django.urls import path
from .views import (home, NewsList, ArticlesList, ArticleDetail, NewsDetail, NewsSearchView,
                    NewsCreateView, NewsUpdateView, NewsDeleteView,
                    ArticleCreateView, ArticleUpdateView, ArticleDeleteView)

urlpatterns = [
    path('', home, name='home'),


    # Маршруты для новостей

    path('news/', NewsList.as_view(), name='news_list'),
    path('news/<int:pk>/', NewsDetail.as_view(), name='news_detail'),
    path('news/search/', NewsSearchView.as_view(), name='news_search'),
    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),

    # Маршруты для статей

    path('articles/', ArticlesList.as_view(), name='articles_list'),
    path('articles/<int:pk>/', ArticleDetail.as_view(), name='article_detail'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
]