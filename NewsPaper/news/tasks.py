import os
from django.urls import reverse
from django.conf import settings

from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category


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