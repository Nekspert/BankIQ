import logging
from datetime import datetime, timedelta

from celery import shared_task
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=6)
def cleanup_old_tokens(self):
    try:
        cutoff = datetime.now() - timedelta(days=30)
        count, _ = OutstandingToken.objects.filter(expires_at__lt=cutoff).delete()
        logger.info(f'[INFO] Cleaned up {count} refresh tokens. '
                    f'Task ID: {self.request.id}. Task retries: {self.request.retries} [INFO]')
    except Exception as exc:
        # При ошибке - повтор через 6 секунд (max 3 попытки)
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc)
