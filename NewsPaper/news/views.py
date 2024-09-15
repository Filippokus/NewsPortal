from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import Post
from .forms import PostForm
from .filters import PostFilter


def home(request):
    return render(request, 'home.html')


class NewsList(ListView):
    model = Post
    ordering = '-date_created'
    template_name = 'news_list.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.filter(post_type='NW').order_by(self.ordering)  # Фильтрация только новостей


class ArticlesList(ListView):
    model = Post
    ordering = '-date_created'
    template_name = 'articles_list.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.filter(post_type='AR').order_by(self.ordering)  # Фильтрация только статей


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news_item'

    def get_queryset(self):
        # Убедимся, что показываем только новости
        return Post.objects.filter(post_type='NW')


class ArticleDetail(DetailView):
    model = Post
    template_name = 'article_detail.html'
    context_object_name = 'article_item'

    def get_queryset(self):
        # Убедимся, что показываем только статьи
        return Post.objects.filter(post_type='AR')


class NewsSearchView(FilterView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    filterset_class = PostFilter


# Создание новости
class NewsCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news_create.html'
    success_url = reverse_lazy('news_list')  # После создания перенаправляем на список новостей

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NW'  # Устанавливаем тип поста как "новость"
        return super().form_valid(form)


# Редактирование новости
class NewsUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'
    success_url = reverse_lazy('news_list')


# Удаление новости
class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')


# Создание статьи
class ArticleCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'article_create.html'
    success_url = reverse_lazy('articles_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'  # Устанавливаем тип поста как "статья"
        return super().form_valid(form)


# Редактирование статьи
class ArticleUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'article_edit.html'
    success_url = reverse_lazy('articles_list')


# Удаление статьи
class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'article_delete.html'
    success_url = reverse_lazy('articles_list')

