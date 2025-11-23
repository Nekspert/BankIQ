import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from banks.models import Bank
from banks.serializers import BankInfoSerializer
from core.helpers.indicators_db_functions import (
    _update_or_create_datetimes_response, _update_or_create_indicators_response)
from core.one_time_tasks import form_f101, form_f123
from core.parsers.soap import all_banks_parser
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from indicators.models import (FormType)


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_all_api_info(self):
    """
    Ежедневная задача:
    - обновляем денежно-кредитную статистику из REST парсера или
    - берём список банков и для каждого запускаем парсеры SOAP
    - сравниваем результаты с БД и обновляем только если поменялось
    :return: None
    """

    started = timezone.now()
    logger.info(f'[!] START update_all_api_info at {started} [!]')

    banks: dict = all_banks_parser.CbrAllBanksParser.parse()
    if 'message' in banks or not banks.get('banks'):
        logger.warning(f'[!!] RETURN EMPTY banks... STOP parsing. Message: {str(banks)} [!!]')
        return
    logger.info(f'[!!!] GOT {len(banks.get('banks', []))} banks [!!!]')

    db_banks = Bank.objects.all()
    banks_map = {b.reg_number: b for b in db_banks}
    database_bank_reg_numbers = set(banks_map.keys())

    for bank_data in banks.get('banks', []):
        reg = bank_data["reg_number"]
        logger.info(f'PARSING data for bank: name={bank_data["name"]}, reg_number={reg}')
        if reg not in database_bank_reg_numbers:
            serializer = BankInfoSerializer(data=bank_data)
            if serializer.is_valid():
                validated = serializer.validated_data
                with transaction.atomic():
                    bank_obj, created = Bank.objects.get_or_create(
                            reg_number=validated['reg_number'],
                            defaults={
                                'bic': validated['bic'],
                                'name': validated['name'],
                                'internal_code': validated['internal_code'],
                                'registration_date': validated['registration_date'],
                                'region_code': validated['region_code'],
                                'tax_id': validated['tax_id'],
                            }
                    )
                    if created:
                        banks_map[bank_obj.reg_number] = bank_obj
                        database_bank_reg_numbers.add(reg)
                        logger.info(f'CREATED new Bank {bank_obj}')
            else:
                logger.warning(f'Bank serializer invalid for bank: name={bank_data["name"]},'
                               f' reg {reg}: {serializer.errors}')
                continue
        else:
            bank_obj = banks_map[reg]

        logger.info(f"{'=' * 10} START PARSE 101 AND 123 FORMS {'=' * 10}")

        form123_obj = FormType.objects.get(title=form_f123()['title'])
        datetimes_data = Form123Parser.get_dates_for_f123(reg)
        if 'message' in datetimes_data or not datetimes_data.get('datetimes'):
            logger.warning(f'[!!] RETURN EMPTY datetimes for form123 and bank {bank_data["name"]}. '
                           f'STOP update datetimes. Message: {str(datetimes_data)} [!!]')
        else:
            created_or_updated, added, removed, datetimes_data = _update_or_create_datetimes_response(
                    bank=bank_obj, form_type=form123_obj, datetimes_obj=datetimes_data)
            if not datetimes_data:
                continue
            logger.info(f'Updated datetimes for form123 and bank {bank_data["name"]} = {created_or_updated}'
                        f' Added = {added}, removed = {removed}')

            for dt in datetimes_data.get('datetimes', []):
                parsed_dt = parse_datetime(dt)
                if parsed_dt is None:
                    logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                    continue
                if timezone.is_aware(parsed_dt):
                    parsed_dt = parsed_dt.replace(tzinfo=None)
                indicators_data = Form123Parser.get_form123_indicators_from_data123(reg, parsed_dt)
                if 'message' in indicators_data:
                    logger.warning("Form123 indicators error for bank %s: %s", reg, indicators_data)
                else:
                    created_or_updated, added, removed, indicators_data = _update_or_create_indicators_response(
                            bank=bank_obj, form_type=form123_obj, indicators_obj=indicators_data, params={
                                'reg_number': reg, 'dt': parsed_dt})
                    if not indicators_data:
                        continue
                    logger.info(f'Updated indicators for form123 and bank {bank_data["name"]} = {created_or_updated}'
                                f' Added = {added}, removed = {removed}')



        form101_obj = FormType.objects.get(title=form_f101()['title'])
        datetimes_data = Form101Parser.get_dates_for_f101(reg)
        if 'message' in datetimes_data or not datetimes_data.get('datetimes'):
            logger.warning(f'[!!] RETURN EMPTY datetimes for form101 and bank {bank_data["name"]}. '
                           f'STOP update datetimes. Message: {str(datetimes_data)} [!!]')
        else:
            created_or_updated, added, removed, datetimes_data = _update_or_create_datetimes_response(
                    bank=bank_obj, form_type=form101_obj, datetimes_obj=datetimes_data)
            if not datetimes_data:
                continue
            logger.info(f'Updated datetimes for form101 and bank {bank_data["name"]} = {created_or_updated}'
                        f' Added = {added}, removed = {removed}')

            for dt in datetimes_data.get('datetimes', []):
                parsed_dt = parse_datetime(dt)
                if parsed_dt is None:
                    logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                    continue
                if timezone.is_aware(parsed_dt):
                    parsed_dt = parsed_dt.replace(tzinfo=None)
                indicators_data = Form101Parser.get_form101_indicators_from_data101(reg, parsed_dt)
                if 'message' in indicators_data:
                    logger.warning("Form101 indicators error for bank %s: %s", reg, indicators_data)
                else:
                    created_or_updated, added, removed, indicators_data = _update_or_create_indicators_response(
                            bank=bank_obj, form_type=form101_obj, indicators_obj=indicators_data, params={
                                'reg_number': reg, 'dt': parsed_dt})
                    if not indicators_data:
                        continue
                    logger.info(f'Updated indicators for form101 and bank {bank_data["name"]} = {created_or_updated}'
                                f' Added = {added}, removed = {removed}')

