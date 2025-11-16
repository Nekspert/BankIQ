from datetime import datetime

from django.db import IntegrityError, transaction

from core.parsers.soap.all_banks_parser import CbrAllBanksParser
from indicators.models import Bank, BankDatesRequest, BankIndicatorDataRequest, BankIndicatorsRequest, FormType
from indicators.serializers import BankInfoSerializer


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
        obj = _find_existing_dates_request(bank, form_type, params)
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
