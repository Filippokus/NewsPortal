from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.urls import reverse_lazy

from django.views import View
from django.contrib.auth.models import Group
from django.shortcuts import redirect

from allauth.account.views import SignupView

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем флаг is_author в контекст
        context['is_author'] = self.request.user.groups.filter(name='authors').exists()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


class NewsSearchView(FilterView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    filterset_class = PostFilter


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
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


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
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


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    success_url = reverse_lazy('post_list')

    def get_template_names(self):
        if self.object.post_type == 'NW':
            return ['news_delete.html']
        elif self.object.post_type == 'AR':
            return ['article_delete.html']
        return super().get_template_names()

    success_url = reverse_lazy('post_list')


class BecomeAuthorView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        authors_group, created = Group.objects.get_or_create(name='authors')  # Получаем или создаем группу `authors`
        request.user.groups.add(authors_group)  # Добавляем текущего пользователя в группу `authors`
        return redirect('post_list')  # Перенаправляем на список постов или другую страницу
