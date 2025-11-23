from datetime import datetime

from django.db import IntegrityError, transaction

from banks.models import Bank, BankDatesRequest, BankDatesResponse
from banks.serializers import BankInfoSerializer
from core.parsers.soap.all_banks_parser import CbrAllBanksParser
from core.utils.hash_utils import canonical_obj_and_hash
from indicators.models import BankIndicatorDataRequest, BankIndicatorsRequest, BankIndicatorsResponse, FormType


def _get_all_banks_from_db():
    q = Bank.objects.all()
    if not q.exists():
        return None
    return {'banks': q}


def _create_banks_from_api():
    data = CbrAllBanksParser.parse()
    if 'message' in data:
        return data

    saved_banks = []
    for bank_data in data.get('banks', []):
        serializer = BankInfoSerializer(data=bank_data)
        if serializer.is_valid():
            validated = serializer.validated_data
            reg_number = validated['reg_number']
            try:
                with transaction.atomic():
                    obj, created = Bank.objects.get_or_create(
                            reg_number=reg_number,
                            defaults={
                                'bic': validated['bic'],
                                'name': validated['name'],
                                'internal_code': validated['internal_code'],
                                'registration_date': validated['registration_date'],
                                'region_code': validated['region_code'],
                                'tax_id': validated['tax_id'],
                            }
                    )
                saved_banks.append(serializer.data)
            except (ValueError, IntegrityError):
                continue

    return {'banks': saved_banks}


def _find_existing_dates_request(bank: Bank, form_type: FormType, params: dict) -> BankDatesRequest:
    return BankDatesRequest.objects.filter(
            bank=bank,
            form_type=form_type,
            reg_number=params.get('reg_number')
    ).select_related('response').first()


def _create_or_get_datetimes_request_atomic(bank: Bank, form_type: FormType, params: dict) -> BankDatesRequest:
    try:
        with transaction.atomic():
            obj, created = BankDatesRequest.objects.get_or_create(
                    bank=bank,
                    form_type=form_type,
                    reg_number=params.get('reg_number')
            )
    except IntegrityError:
        obj = _find_existing_dates_request(bank, form_type, params)
    return obj


def _find_existing_indicators_request(bank: Bank, form_type: FormType, params: dict) -> BankIndicatorsRequest:
    return BankIndicatorsRequest.objects.filter(
            bank=bank,
            form_type=form_type,
            reg_number=params.get('reg_number'),
            dt=params.get('dt')).first()


def _create_or_get_indicators_request_atomic(bank: Bank, form_type: FormType, params: dict):
    try:
        with transaction.atomic():
            obj, created = BankIndicatorsRequest.objects.get_or_create(
                    bank=bank,
                    form_type=form_type,
                    reg_number=params.get('reg_number'),
                    dt=params.get('dt')
            )
    except IntegrityError:
        obj = _find_existing_indicators_request(bank, form_type, params)
    return obj


def _find_existing_bank_indicators_data_request(bank: Bank, form_type: FormType, reg_number: int,
                                                ind_code: str | None = None,
                                                date_from: datetime | None = None, date_to: datetime | None = None,
                                                dt: datetime | None = None) -> BankIndicatorDataRequest:
    return BankIndicatorDataRequest.objects.filter(
            bank=bank,
            form_type=form_type,
            reg_number=reg_number,
            ind_code=ind_code,
            date_from=date_from,
            date_to=date_to,
            dt=dt).first()


def _create_or_get_bank_indicators_data_request_atomic(bank: Bank, form_type: FormType,
                                                       reg_number: int, ind_code: str | None = None,
                                                       date_from: datetime | None = None,
                                                       date_to: datetime | None = None,
                                                       dt: datetime | None = None) -> BankIndicatorDataRequest:
    try:
        with transaction.atomic():
            obj, created = BankIndicatorDataRequest.objects.get_or_create(
                    bank=bank,
                    form_type=form_type,
                    reg_number=reg_number,
                    ind_code=ind_code,
                    date_from=date_from,
                    date_to=date_to,
                    dt=dt)
    except IntegrityError:
        obj = _find_existing_bank_indicators_data_request(reg_number, ind_code, date_from, date_to)
    return obj


def _update_or_create_datetimes_response(bank: Bank,
                                         form_type: FormType,
                                         datetimes_obj) -> tuple[bool, list[str], list[str], dict]:
    """
    datetimes_obj — python-структура (list/dict) возвращаемая сериализатором/парсером.
    Создаёт/обновляет BankDatesRequest и BankDatesResponse, только если hash изменился.
    Возвращает tuple (created_or_updated: bool, added_dates:list, removed_dates:list)
    """
    req = _create_or_get_datetimes_request_atomic(bank, form_type, {'reg_number': bank.reg_number})

    canonical_obj, new_hash = canonical_obj_and_hash(datetimes_obj)

    with transaction.atomic():
        req_locked = BankDatesRequest.objects.select_for_update().get(pk=req.pk)
        existing_resp = getattr(req_locked, 'response', None)
        if existing_resp and getattr(existing_resp, 'data_hash', None) == new_hash:
            return False, [], [], canonical_obj
        old = existing_resp.datetimes if existing_resp else None
        if existing_resp:
            existing_resp.datetimes = canonical_obj
            existing_resp.data_hash = new_hash
            existing_resp.save(update_fields=['datetimes', 'data_hash', 'updated_at'])
            created_or_updated = True
        else:
            BankDatesResponse.objects.create(request=req_locked, datetimes=canonical_obj, data_hash=new_hash)
            created_or_updated = True

    try:
        old_set = set(old.get('datetimes', []) or [])
        new_set = set(canonical_obj.get('datetimes', []) or [])
        added = sorted(list(new_set - old_set))
        removed = sorted(list(old_set - new_set))
    except Exception:
        added = []
        removed = []

    return created_or_updated, added, removed, canonical_obj


def _update_or_create_indicators_response(
        bank: Bank,
        form_type: FormType,
        params: dict,
        indicators_obj: dict) -> tuple[bool, list[str], list[str], dict]:
    """
    Обновляет/создаёт BankIndicatorsResponse для данного request (bank+form_type+params),
    только если digest изменился.

    params: должен содержать ключи, используемые _create_or_get_indicators_request_atomic (reg_number, dt)
    indicators_obj: python-структура, возвращаемая парсером {'indicators': [...]}

    Возвращает: (created_or_updated, added_codes, removed_codes, canonical_obj)
    - created_or_updated: True если создано или обновлено
    - added_codes / removed_codes: списки ind_code, которые добавились/удалились (если возможно выделить)
    - canonical_obj: нормализованный объект (подходит для записи в JSONField)
    """
    req = _create_or_get_indicators_request_atomic(bank=bank, form_type=form_type, params=params)

    canonical_obj, new_hash = canonical_obj_and_hash(indicators_obj)

    with transaction.atomic():
        req_locked = BankIndicatorsRequest.objects.select_for_update().get(pk=req.pk)
        existing_resp = getattr(req_locked, 'response', None)
        if existing_resp and getattr(existing_resp, 'data_hash', None) == new_hash:
            return False, [], [], canonical_obj
        old_indicators = []
        if existing_resp:
            old_indicators = getattr(existing_resp, 'indicators', []) or []

            existing_resp.indicators = canonical_obj
            existing_resp.data_hash = new_hash
            existing_resp.save(update_fields=['indicators', 'data_hash', 'updated_at'])
            created_or_updated = True
        else:
            BankIndicatorsResponse.objects.create(request=req_locked, indicators=canonical_obj, data_hash=new_hash)
            created_or_updated = True

    try:
        old_codes = {item.get('ind_code') for item in old_indicators if
                     isinstance(item, dict) and item.get('ind_code') is not None}
        new_codes = {item.get('ind_code') for item in canonical_obj.get('indicators', []) if
                     isinstance(item, dict) and item.get('ind_code') is not None}
        added = sorted(list(new_codes - old_codes))
        removed = sorted(list(old_codes - new_codes))
    except Exception:
        added = []
        removed = []

    return created_or_updated, added, removed, canonical_obj
