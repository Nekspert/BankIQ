import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import beat_init


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_iq.settings')
app = Celery('bank_iq')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'monthly-parsers-update-reports-api-info': {
        'task': 'core.tasks.update_all_reports_api_info',
        'schedule': crontab(minute=0, hour=0, day_of_month='1'),
    },
    'monthly-parsers-update-bank-api-info': {
        'task': 'core.tasks.update_all_bank_api_info',
        'schedule': crontab(minute=0, hour=0, day_of_month='1'),
    },
    'daily-cleanup-tokens': {
        'task': 'accounts.tasks.cleanup_old_tokens',
        'schedule': crontab(hour=0, day_of_week=1),
    }
}


@beat_init.connect
def send_initial_task(sender, **kwargs):
    from core.tasks import update_all_bank_api_info, update_all_reports_api_info
    try:
        update_all_reports_api_info.apply_async()
        update_all_bank_api_info.apply_async(countdown=30)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception('Failed to enqueue initial monthly tasks: %s', e)
