# core/utils/hash_utils.py
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Tuple


def _normalize_value(v: Any):
    if isinstance(v, Decimal):
        return format(v, 'f')
    if isinstance(v, datetime):
        if v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v.isoformat()
    if isinstance(v, dict):
        return {k: _normalize_value(v[k]) for k in sorted(v)}
    if isinstance(v, (list, tuple)):
        return [_normalize_value(x) for x in v]
    return v


def canonical_obj_and_hash(obj: Any) -> Tuple[dict, str]:
    """
    Возвращает (canonical_obj_as_python, sha256_hex).
    canonical_obj_as_python — это нормализованный python-объект (dict/list) готовый для JSONField.
    """
    normalized = _normalize_value(obj)
    json_text = json.dumps(normalized, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    h = hashlib.sha256(json_text.encode()).hexdigest()
    return normalized, h
