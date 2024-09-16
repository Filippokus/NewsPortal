from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from .models import Post
from .forms import PostForm
from .filters import PostFilter


class PostListView(ListView):
    model = Post
    ordering = '-date_created'
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.all().order_by(self.ordering)


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


class NewsSearchView(FilterView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    filterset_class = PostFilter


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post_list')

    def get_template_names(self):
        if 'news' in self.request.path:
            return ['news_create.html']  # Шаблон для создания новости
        elif 'articles' in self.request.path:
            return ['article_create.html']  # Шаблон для создания статьи

    def form_valid(self, form):
        post = form.save(commit=False)
        # Определяем тип поста на основе URL
        if 'news' in self.request.path:
            post.post_type = 'NW'
        elif 'articles' in self.request.path:
            post.post_type = 'AR'
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    login_url = '/login/'
    success_url = reverse_lazy('post_list')

    def get_template_names(self):
        if self.object.post_type == 'NW':
            return ['news_edit.html']
        elif self.object.post_type == 'AR':
            return ['article_edit.html']
        return super().get_template_names()


class PostDeleteView(DeleteView):
    model = Post

    def get_template_names(self):
        if self.object.post_type == 'NW':
            return ['news_delete.html']
        elif self.object.post_type == 'AR':
            return ['article_delete.html']
        return super().get_template_names()

    success_url = reverse_lazy('post_list')
