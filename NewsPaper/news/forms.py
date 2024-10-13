from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'author']  # Поля, которые пользователь должен заполнять


class CustomSignupForm(SignupForm):

    def save(self, request):
        # Сохраняем пользователя через форму allauth
        user = super(CustomSignupForm, self).save(request)
        # Получаем или создаем группу common
        common_group, created = Group.objects.get_or_create(name='common')
        # Добавляем нового пользователя в группу common
        common_group.user_set.add(user)
        return user