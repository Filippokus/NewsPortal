from django.views.generic import ListView, DetailView
from .models import Post


class NewsList(ListView):
    model = Post
    ordering = '-date_created'
    template_name = 'news_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(post_type__in=['AR', 'NW']).order_by(self.ordering)


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news_item'
