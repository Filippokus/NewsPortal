from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseServerError  # Импорт для тестовой ошибки

# Функция для тестирования логов ошибок
def test_error(request):
    raise Exception("This is a test error")  # Исключение уровня ERROR

urlpatterns = [
    path('accounts/', include('allauth.urls')),  # Маршруты allauth
    path('sign/', include('sign.urls')),
    path('admin/', admin.site.urls),
    path('', include('news.urls')),
    path('error/', test_error, name='test_error'),  # Новый маршрут для тестирования
]