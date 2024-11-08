import logging
import os
from django.urls import reverse
from django.conf import settings

from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category

from celery import shared_task

logger = logging.getLogger(__name__)

def send_weekly_news():
    """
    Отправляет еженедельное письмо с новыми постами подписчикам категорий.
    """

    # Получаем текущую дату и дату неделю назад
    one_week_ago = now() - timedelta(days=7)

    # Получаем все посты, созданные за последнюю неделю
    recent_posts = Post.objects.filter(date_created__gte=one_week_ago)

    # Получаем все категории с подписчиками и постами
    categories = Category.objects.prefetch_related('subscribers', 'post_set')

    for category in categories:
        # Получаем посты за неделю в конкретной категории
        posts_in_category = recent_posts.filter(categories=category)

        if posts_in_category.exists():
            subscribers = category.subscribers.all()

            for subscriber in subscribers:
                # Генерируем ссылки для постов
                posts_with_urls = [
                    (post, f"{settings.SITE_URL}{reverse('post_detail', kwargs={'pk': post.pk})}")
                    for post in posts_in_category
                ]

                # Формируем письмо для каждого подписчика
                subject = f"Новые статьи в категории {category.name} за неделю"

                # HTML-содержимое
                html_content = render_to_string('email/weekly_news.html', {
                    'subscriber': subscriber,
                    'category': category,
                    'posts_with_urls': posts_with_urls
                })

                # Текстовое содержимое письма
                text_content = (f"Привет, {subscriber.username}! "
                                f"Вот новые статьи за прошедшую неделю в категории {category.name}:")

                # Отправка письма
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=f"{os.getenv('EMAIL_HOST_USER_LOCAL')}@{os.getenv('EMAIL_DOMAIN')}",
                    to=[subscriber.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)


@shared_task
def notify_subscriber_about_post(post_id, subscriber_email, subscriber_username):
    print(f"Задача Celery запущена для: {subscriber_email}")  # Отладочный вывод
    from .models import Post  # Импорт модели Post

    try:
        # Получаем объект поста
        post = Post.objects.get(pk=post_id)

        # Формируем тему письма и HTML-содержимое
        subject = post.title
        post_url = f"{settings.SITE_URL}{reverse('post_detail', kwargs={'pk': post.pk})}"
        html_content = render_to_string(
            'email/new_post_email.html',
            {'post': post, 'username': subscriber_username, 'post_url': post_url}
        )
        text_content = (f"Здравствуй, {subscriber_username}. "
                        f"Новая статья в твоём любимом разделе! Перейди по ссылке для просмотра: {post_url}")

        # Отправка письма
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,  # Текстовая версия письма
            from_email=f"{os.getenv('EMAIL_HOST_USER_LOCAL')}@{os.getenv('EMAIL_DOMAIN')}",
            to=[subscriber_email]
        )
        msg.attach_alternative(html_content, "text/html")  # HTML версия письма
        msg.send(fail_silently=False)

        logger.info(f"Письмо успешно отправлено {subscriber_email}")

    except Exception as e:
        logger.error(f"Ошибка при отправке письма для {subscriber_email}: {e}")


@shared_task
def send_weekly_newsletter():
    last_week = now() - timedelta(days=7)
    recent_posts = Post.objects.filter(date_created__gte=last_week)

    if recent_posts.exists():
        # Получаем всех уникальных подписчиков из всех категорий
        subscribers = set()
        categories = Category.objects.all()
        for category in categories:
            for subscriber in category.subscribers.all():
                subscribers.add(subscriber)  # Добавляем подписчика в множество, чтобы избежать дублирования

        # Формируем и отправляем рассылку каждому подписчику
        for subscriber in subscribers:
            subject = "Еженедельная рассылка новостей"
            # Формируем текстовую версию
            text_content = "Последние новости за неделю:\n\n" + "\n".join(
                [f"{post.title} - {post.text[:100]}..." for post in recent_posts]
            )
            # Формируем HTML-версию с помощью шаблона
            html_content = render_to_string("email/weekly_newsletter.html", {"posts": recent_posts, "username": subscriber.username})

            # Настройка письма
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,  # Текстовая версия письма
                from_email=f"{os.getenv('EMAIL_HOST_USER_LOCAL')}@{os.getenv('EMAIL_DOMAIN')}",
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, "text/html")  # HTML-версия письма
            msg.send(fail_silently=False)


# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_jobstore(DjangoJobStore(), 'default')
#
#     # Добавляем задачу для еженедельной отправки
#     scheduler.add_job(
#         send_weekly_news,
#         trigger='cron',  # Еженедельно
#         day_of_week='sun',  # Каждое воскресенье
#         hour=10,  # В 10 утра
#         minute=0,
#         id='weekly_news_job',
#         replace_existing=True
#     )
#
#     scheduler.start()