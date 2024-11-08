import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.template.loader import render_to_string
import os

from django.urls import reverse
from django.conf import settings

from .models import Post
from .tasks import notify_subscriber_about_post

logger = logging.getLogger(__name__)


@receiver(user_signed_up)
def send_welcome_email(sender, request, user, **kwargs):
    """
    Отправляет приветственное письмо пользователю после успешной регистрации.

    Параметры:
    - sender: отправитель сигнала
    - request: текущий запрос, связанный с регистрацией пользователя
    - user: объект пользователя, который только что зарегистрировался
    - kwargs: дополнительные аргументы, которые передаются сигналом

    Процесс:
    1. Формируется заголовок письма и его HTML-содержимое, содержащее имя пользователя.
    2. Отправляется письмо с текстовой и HTML-версиями.
    """
    # Формируем тему письма и содержимое
    subject = f"Добро пожаловать, {user.username}!"
    context = {'username': user.username}
    html_content = render_to_string('email/welcome_email.html', context)
    text_content = f"Здравствуйте, {user.username}! Спасибо за регистрацию на нашем сайте."

    # Отправляем письмо
    send_mail(
        subject=subject,
        message=text_content,  # Текстовая версия письма
        from_email=f"{os.getenv('EMAIL_HOST_USER_LOCAL')}@{os.getenv('EMAIL_DOMAIN')}",
        recipient_list=[user.email],  # Адрес получателя
        fail_silently=False,
        html_message=html_content  # HTML версия письма
    )


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_on_category_change(sender, instance, action, **kwargs):
    """
    Уведомляет подписчиков, если были добавлены категории к посту.
    """
    if action == 'post_add':  # Отслеживаем только момент, когда категории добавляются к посту
        post = instance
        categories = post.categories.all()

        logger.info(f"Пост '{post.title}' был сохранен. Обновление подписчиков по категориям.")
        print(f"Категории поста: {[category.name for category in categories]}")

        for category in categories:
            subscribers = category.subscribers.all()
            print(f"Категория: {category.name}, подписчики: {subscribers.count()}")

            if not subscribers:
                logger.info(f"У категории '{category.name}' нет подписчиков.")
            else:
                logger.info(f"Категория '{category.name}' имеет {subscribers.count()} подписчиков.")

                for subscriber in subscribers:
                    logger.info(f"Отправка задачи для подписчика: {subscriber.email}")
                    # Запуск задачи через Celery с использованием delay() и передачей данных
                    notify_subscriber_about_post.delay(post.pk, subscriber.email, subscriber.username)