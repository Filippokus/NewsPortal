import django_filters
from .models import Post
from django import forms


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Название')
    author = django_filters.CharFilter(field_name='author__user__username', lookup_expr='icontains', label='Автор')
    date_after = django_filters.DateFilter(
        field_name='date_created',
        lookup_expr='gt',
        label='Дата после',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = ['title', 'author', 'date_after']
