from django.contrib.auth.models import Group


def is_author(request):
    if request.user.is_authenticated:
        return {'is_author': request.user.groups.filter(name='authors').exists()}
    return {'is_author': False}