import hashlib
import logging
from io import BytesIO
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

from .minio import ensure_bucket_exists, get_s3_storage


logger = logging.getLogger(__name__)


def user_avatar_upload_path(instance, filename, use_user: bool = True):
    if use_user:
        return f"users/{instance.user.id}/{filename}"
    return f"users/{instance}/{filename}"


def _get_gravatar_url(email, size=512, default="identicon", rating="pg") -> str:
    """
    Генерирует URL для Gravatar

    Args:
        email (str): Email пользователя
        size (int): Размер изображения в пикселях (1-2048)
        default (str): Тип изображения по умолчанию:
            - '404': возвращает 404 если нет аватара
            - 'mp': mystery-person (силуэт)
            - 'identicon': геометрический паттерн (по умолчанию)
            - 'monsterid': монстрики
            - 'wavatar': лица с разными чертами
            - 'retro': 8-битные пиксельные лица
            - 'robohash': роботы
            - 'blank': прозрачный PNG
        rating (str): Рейтинг контента:
            - 'g': подходит всем
            - 'pg': родительский контроль
            - 'r': ограниченный
            - 'x': только для взрослых
    """
    email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
    params = {'s': size, 'r': rating, 'd': default}

    query_string = urlencode(params)
    url = f"https://www.gravatar.com/avatar/{email_hash}?{query_string}"
    return url


def generate_gravatar_avatar(user, size=512) -> str | None:
    """
    Генерирует URL для Gravatar
    Args:
        email (str): Email пользователя
        size (int): Размер изображения в пикселях (1-2048)
        default (str): Тип изображения по умолчанию:
            - '404': возвращает 404 если нет аватара
            - 'mp': mystery-person (силуэт)
            - 'identicon': геометрический паттерн (по умолчанию)
            - 'monsterid': монстрики
            - 'wavatar': лица с разными чертами
            - 'retro': 8-битные пиксельные лица
            - 'robohash': роботы
            - 'blank': прозрачный PNG
        rating (str): Рейтинг контента:
            - 'g': подходит всем
            - 'pg': родительский контроль
            - 'r': ограниченный
            - 'x': только для взрослых
    """

    logger.info("generate_gravatar_avatar called for user id=%s, email=%s",
                getattr(user, "id", None), getattr(user, "email", None))

    try:
        email = getattr(user, "email", None)
        if not email:
            raise ValueError("У пользователя нет email адреса")

        s3_storage = get_s3_storage()
        bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)

        if bucket:
            created = ensure_bucket_exists(bucket)
            if not created:
                logger.error("Bucket %s does not exist and could not be created — abort saving avatar", bucket)
                return None

        logger.info(f"Использую S3 хранилище для пользователя {user.id}")
        logger.info(f"Бакет: {s3_storage.bucket_name}")
        logger.info(f"Endpoint: {settings.AWS_S3_ENDPOINT_URL}")

        gravatar_url = _get_gravatar_url(email=email, size=size)
        response = requests.get(gravatar_url, timeout=10)
        response.raise_for_status()
        image_content = BytesIO(response.content)
        image = Image.open(image_content)

        output_buffer = BytesIO()
        image.save(output_buffer, format="PNG", quality=95)
        output_buffer.seek(0)

        # Формируем путь в S3
        filename = f"avatar_{size}x{size}.png"
        s3_key = user_avatar_upload_path(instance=user.id, filename=filename, use_user=False)

        logger.info(f"Сохранение в S3: {s3_key}")

        # Сохраняем в S3
        content = ContentFile(output_buffer.read())
        saved_key = s3_storage.save(s3_key, content)

        # Проверяем, что файл сохранен
        exists = s3_storage.exists(saved_key)
        logger.info(f"Файл сохранен: {saved_key}, существует: {exists}")

        if exists:
            try:
                url = s3_storage.url(saved_key)
                logger.info(f"URL файла в S3: {url}")
            except Exception as e:
                logger.warning(f"Не удалось получить URL: {e}")

            return saved_key
        else:
            logger.error("Файл не найден в S3 после сохранения!")
            return None

    except requests.RequestException as e:
        logger.error(f"[WARN] Gravatar request failed: {e} [WARN]", exc_info=True)
    except Exception as e:
        logger.error(f"[WARN] Error in generate_gravatar_avatar: {e} [WARN]", exc_info=True)
