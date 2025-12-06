import re
import uuid

from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()


def _normalize_name_part(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\-_.]", "", slugify(s or "")) or ""


def generate_username_from_names(first_name: str | None, last_name: str | None, max_len: int = 30) -> str:
    """
    Генерирует уникальный username в формате slug из first_name + last_name.
    Поведение:
      - объединяет first и last в 'first-last' (slugify -> ascii)
      - если пусто, генерирует short uuid (без дефисов)
      - проверяет уникальность в БД; при коллизии добавляет суффикс: name, name1, name2...
    Ограничение длины: max_len (по умолчанию 30, подходит для стандартной модели).
    """
    base_parts = []
    if first_name:
        base_parts.append(_normalize_name_part(first_name))
    if last_name:
        base_parts.append(_normalize_name_part(last_name))
    if base_parts:
        base = "-".join([p for p in base_parts if p])  # "ivan-ivanov"
    else:
        base = uuid.uuid4().hex[:8]

    # ensure within max_len (reserve 4 chars for suffix)
    if len(base) > max_len - 4:
        base = base[: max_len - 4]

    candidate = base
    inc = 0
    while User.objects.filter(username=candidate).exists():
        inc += 1
        suffix = str(inc)
        trim_len = max_len - len(suffix) - 1  # one for separator
        trimmed = base if len(base) <= trim_len else base[:trim_len]
        candidate = f"{trimmed}-{suffix}"
    return candidate
