import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-weekly-newsletter': {
        'task': 'news.tasks.send_weekly_newsletter',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Понедельник в 8:00 утра
    },
}