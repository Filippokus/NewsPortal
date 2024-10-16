import logging


from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages

from django.views import View
from django.contrib.auth.models import Group
from django.shortcuts import redirect

from .models import Post, Author, Category
from .forms import PostForm
from .filters import PostFilter


logger = logging.getLogger(__name__)


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
    """
    Представление для создания постов. Включает проверки на наличие категорий и ограничение
    количества постов, которые пользователь может создать за один день.
    В зависимости от URL, пост может быть новостью или статьей.

    Атрибуты:
    - permission_required: требуется разрешение на добавление постов.
    - model: модель Post, с которой работает представление.
    - form_class: форма, которая используется для создания поста.
    - success_url: URL для перенаправления при успешном создании поста.
    """

    permission_required = ('news.add_post',)
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post_list')

    def get_template_names(self):
        """
        Определяет, какой шаблон использовать в зависимости от пути URL.
        Если в пути содержится 'news', то используется шаблон для создания новости.
        Если в пути содержится 'articles', то используется шаблон для создания статьи.

        Возвращает:
        - Строку с именем шаблона.
        """
        if 'news' in self.request.path:
            return ['news_create.html']
        elif 'articles' in self.request.path:
            return ['article_create.html']

    def determine_post_type(self, post):
        """
        Определяет тип поста на основе URL.
        Если URL содержит 'news', пост будет типа 'NW' (новость).
        Если URL содержит 'articles', пост будет типа 'AR' (статья).

        Аргументы:
        - post: объект поста, для которого устанавливается тип.

        Возвращает:
        - Объект поста с установленным типом.
        """
        if 'news' in self.request.path:
            post.post_type = 'NW'
        elif 'articles' in self.request.path:
            post.post_type = 'AR'
        return post

    def assign_author(self, post):
        """
        Назначает автором поста текущего пользователя.
        Если автор для пользователя не найден, возникает ошибка.

        Аргументы:
        - post: объект поста, для которого назначается автор.

        Возвращает:
        - Объект поста с назначенным автором.
        """
        try:
            post.author = Author.objects.get(user=self.request.user)
        except Author.DoesNotExist:
            logger.error(f"Author does not exist for user: {self.request.user.username}")
            raise
        return post

    def check_daily_post_limit(self):
        """
        Проверяет, сколько постов пользователь уже создал за текущие сутки.
        Пользователь может создать не более трех постов за день.

        Возвращает:
        - True, если лимит не превышен.
        - False, если пользователь уже создал 3 поста за сегодня.
        """
        from django.utils.timezone import now
        today = now().date()

        post_count_today = Post.objects.filter(
            author__user=self.request.user,  # Посты текущего пользователя
            date_created__date=today  # Посты за сегодня
        ).count()

        return post_count_today < 3

    def save_post_and_categories(self, form):
        """
        Сохраняет пост и связанные с ним категории.
        Перед сохранением определяет тип поста и назначает автора.
        Использует form.save_m2m() для сохранения связей Many-to-Many.

        Аргументы:
        - form: форма, из которой создается пост.

        Возвращает:
        - Сохраненный объект поста.
        """
        post = form.save(commit=False)  # Сохраняем объект, но не записываем его в БД
        self.determine_post_type(post)  # Определяем тип поста
        self.assign_author(post)  # Назначаем автора посту
        post.save()  # Сохраняем пост
        form.save_m2m()  # Сохраняем связи Many-to-Many (категории)
        return post

    def form_valid(self, form):
        """
        Выполняет основные проверки и сохранение поста.
        1. Проверяет, не превышен ли лимит на количество постов за день.
        2. Проверяет, что пользователь выбрал хотя бы одну категорию.
        3. Сохраняет пост и связанные категории.

        Аргументы:
        - form: форма, переданная для создания поста.

        Возвращает:
        - Результат вызова super().form_valid(form), если все проверки пройдены.
        """
        # Проверяем лимит постов за текущие сутки
        if not self.check_daily_post_limit():
            messages.error(self.request, 'Вы не можете публиковать более трёх новостей в сутки.')
            return redirect('post_list')

        # Проверка наличия категорий перед сохранением
        if not form.cleaned_data.get('categories'):
            messages.error(self.request, 'Вы должны выбрать хотя бы одну категорию.')
            return self.form_invalid(form)

        post = self.save_post_and_categories(form)  # Сохраняем пост и его категории

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
        # Получаем или создаем группу `authors`
        authors_group, created = Group.objects.get_or_create(name='authors')

        # Добавляем текущего пользователя в группу `authors`
        request.user.groups.add(authors_group)

        # Создаем объект Author, если его еще нет
        Author.objects.get_or_create(user=request.user)

        return redirect('post_list')  # Перенаправляем на список постов или другую страницу


class SubscribeToCategoryView(LoginRequiredMixin, View):
    login_url = '/login/'  # Если пользователь не авторизован, перенаправляем на страницу входа

    def post(self, request, category_id, post_id, *args, **kwargs):
        category = get_object_or_404(Category, id=category_id)  # Получаем категорию по ID
        category.subscribers.add(request.user)  # Добавляем текущего пользователя в подписчики категории
        return redirect('post_detail', pk=post_id)  # Перенаправляем на страницу поста


class UnsubscribeFromCategoryView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, category_id, post_id, *args, **kwargs):
        category = get_object_or_404(Category, id=category_id)  # Получаем категорию
        category.subscribers.remove(request.user)  # Удаляем пользователя из подписчиков
        return redirect('post_detail', pk=post_id)  # Возвращаемся на страницу поста