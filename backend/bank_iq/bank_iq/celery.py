import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import beat_init


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_iq.settings')
app = Celery('bank_iq')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'daily-parsers-update': {
        'task': 'core.tasks.update_all_api_info',
        'schedule': crontab(hour=0, minute=0),
    }
}


@beat_init.connect
def send_initial_task(sender, **kwargs):
    from core.tasks import update_all_api_info
    update_all_api_info.apply_async()
