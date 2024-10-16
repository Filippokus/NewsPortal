from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django import forms
from .models import Post, Category, Author


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'categories']  # Поля, которые пользователь должен заполнять


class CustomSignupForm(SignupForm):

    def save(self, request):
        # Сохраняем пользователя через форму allauth
        user = super(CustomSignupForm, self).save(request)
        # Получаем или создаем группу common
        common_group, created = Group.objects.get_or_create(name='common')
        # Добавляем нового пользователя в группу common
        common_group.user_set.add(user)
        return user