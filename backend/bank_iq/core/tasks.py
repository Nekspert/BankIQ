import logging
from concurrent.futures import as_completed, ThreadPoolExecutor
from datetime import datetime

from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from banks.models import Bank
from banks.serializers import BankInfoSerializer
from core.helpers.indicators_db_functions import (
    _update_or_create_bank_indicator_data_response, _update_or_create_datetimes_response,
    _update_or_create_indicators_response)
from core.helpers.reports_db_functions import _create_or_get_request_atomic
from core.one_time_tasks import form_f101, form_f123, form_f810
from core.parsers.rest.cbr_parser import CbrAPIParser
from core.parsers.soap import all_banks_parser
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from core.parsers.soap.form810_parser import Form810Parser
from indicators.models import (FormType)
from reports.models import CbrApiDataRequest, CbrApiDataResponse
from reports.serializers import CheckResponseSerializer, CheckYearsResponseSerializer, ResponseSerializer


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_all_bank_api_info(self):
    """
    Месячная задача:
    - обновляем денежно-кредитную статистику из REST парсера или
    - берём список банков и для каждого запускаем парсеры SOAP
    - сравниваем результаты с БД и обновляем только если поменялось
    :return: None
    """

    started = timezone.now()
    logger.info(f'[!] START update_all_bank_api_info at {started} [!]')

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

        logger.info(f"{'=' * 10} START PARSE 101, 123, 810 FORMS {'=' * 10}")

        def generate_f810_dates(start_year: int = 2000, end_year: int | None = None) -> list[str]:
            """
            Генерирует ISO-строки для дат 1 января и 1 апреля каждого года в диапазоне.
            Формат: "YYYY-MM-DDT00:00:00Z" (timezone-aware строка с Z).
            По умолчанию: с 2000 по текущий год (в часовом поясе Django).
            """
            if end_year is None:
                # берем текущий год в том часовом поясе, который использует Django
                end_year = timezone.now().year

            dates: list[str] = []
            for y in range(start_year, end_year + 1):
                dates.append(f"{y:04d}-01-01T00:00:00Z")
                dates.append(f"{y:04d}-04-01T00:00:00Z")
            return dates

        form810_obj = FormType.objects.get(title=form_f810()['title'])
        f810_dates_iso = generate_f810_dates()

        for dt in f810_dates_iso:
            parsed_dt = parse_datetime(dt)
            if parsed_dt is None:
                logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                continue
            if timezone.is_aware(parsed_dt):
                parsed_dt = parsed_dt.replace(tzinfo=None)

            bank_indicator_data = Form810Parser.parse(reg, parsed_dt)
            if 'message' in bank_indicator_data or not bank_indicator_data:
                logger.warning(
                        f'[!!] RETURN EMPTY bank indicator data for form810 and bank {bank_data["name"]}. '
                        f'STOP update bank indicator data. Message: {str(bank_indicator_data)} [!!]')
            else:
                created_or_updated, added, removed, canonical_obj = _update_or_create_bank_indicator_data_response(
                        bank=bank_obj,
                        form_type=form810_obj,
                        bank_indicator_obj=bank_indicator_data,
                        params={'reg_number': reg, 'dt': parsed_dt}
                )
                logger.debug(
                        "Saved F810 for bank %s dt=%s -> upd=%s added=%d removed=%d",
                        bank_data['name'], parsed_dt.isoformat(), created_or_updated,
                        len(added) if added is not None else 0,
                        len(removed) if removed is not None else 0
                )

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
            logger.debug(f'Updated datetimes for form123 and bank {bank_data["name"]} = {created_or_updated}'
                        f' Added = {added}, removed = {removed}')

            for dt in datetimes_data.get('datetimes', []):
                parsed_dt = parse_datetime(dt)
                if parsed_dt is None:
                    logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                    continue
                if timezone.is_aware(parsed_dt):
                    parsed_dt = parsed_dt.replace(tzinfo=None)
                indicators_data = Form123Parser.get_form123_indicators_from_data123(reg, parsed_dt)
                if 'message' in indicators_data or not indicators_data.get('indicators'):
                    logger.warning(f'[!!] RETURN EMPTY indicators for form123 and bank {bank_data["name"]}. '
                                   f'STOP update indicators. Message: {str(indicators_data)} [!!]')
                else:
                    created_or_updated, added, removed, indicators_data = _update_or_create_indicators_response(
                            bank=bank_obj, form_type=form123_obj, indicators_obj=indicators_data, params={
                                'reg_number': reg, 'dt': parsed_dt})
                    if not indicators_data:
                        continue
                    logger.debug(f'Updated indicators for form123 and bank {bank_data["name"]} = {created_or_updated}'
                                f' Added = {added}, removed = {removed}')

                    bank_indicator_data = Form123Parser.get_data123_form_full(reg, dt)
                    if 'message' in bank_indicator_data or not bank_indicator_data:
                        logger.warning(
                                f'[!!] RETURN EMPTY bank indicator data for form123 and bank {bank_data["name"]}. '
                                f'STOP update bank indicator data. Message: {str(bank_indicator_data)} [!!]')
                    else:
                        created_or_updated, added, removed, bank_indicator_data = (
                            _update_or_create_bank_indicator_data_response(bank=bank_obj, form_type=form123_obj,
                                                                           bank_indicator_obj=bank_indicator_data,
                                                                           params={'reg_number': reg, 'dt': parsed_dt}))
                        if not bank_indicator_data:
                            continue
                        logger.debug(
                                f'Updated bank indicator data for form123 and bank {bank_data["name"]} = {created_or_updated}'
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
            logger.debug(f'Updated datetimes for form101 and bank {bank_data["name"]} = {created_or_updated}'
                        f' Added = {added}, removed = {removed}')

            MAX_WORKERS = 10  # число потоков для параллельных запросов
            BATCH_SUBMIT = 300  # сколько задач отправлять в пул за раз

            indicators_map: dict[str, set[datetime] | list[datetime]] = {}
            unique_codes = set()
            for dt in datetimes_data.get('datetimes', []):
                parsed_dt = parse_datetime(dt)
                if parsed_dt is None:
                    logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                    continue
                if timezone.is_aware(parsed_dt):
                    parsed_dt = parsed_dt.replace(tzinfo=None)
                indicators_data = Form101Parser.get_form101_indicators_from_data101(reg, parsed_dt)
                if 'message' in indicators_data or not indicators_data.get('indicators'):
                    logger.warning(f'[!!] RETURN EMPTY indicators for form101 and bank {bank_data["name"]}. '
                                   f'STOP update indicators. Message: {str(indicators_data)} [!!]')
                else:
                    for ind in indicators_data.get('indicators', []):
                        code = ind.get('ind_code')
                        if not code:
                            continue
                        if code not in unique_codes:
                            unique_codes.add(code)
                            indicators_map.setdefault(code, []).append(parsed_dt)

            def generate_all_pairs(dates_list):
                length = len(dates_list)
                for i in range(length):
                    di = dates_list[i]
                    for j in range(i, length):
                        yield di, dates_list[j]

            fetch_cache: dict[tuple, list] = {}

            def _fetch_range(bank_reg, ind_code_local, date_from, date_to):
                """
                Возвращает (key, payload) — key для кеша, payload: list|dict (если ошибка — dict с 'message').
                """
                key = (ind_code_local, date_from.isoformat(), date_to.isoformat())
                if key in fetch_cache:
                    return key, fetch_cache[key]
                try:
                    res = Form101Parser.get_indicator_data(reg_number=bank_reg,
                                                           ind_code=ind_code_local,
                                                           date_from=date_from,
                                                           date_to=date_to)
                except Exception as e:
                    res = {'message': f'exception: {e}'}
                fetch_cache[key] = res
                return key, res

            for ind_code, dates_sorted in indicators_map.items():
                if not dates_sorted:
                    continue

                dates_sorted = [i for i in dates_sorted if i.year >= 2018]

                n = len(dates_sorted)
                pair_count = n * (n + 1) // 2
                logger.debug('Indicator %s: %d dates -> %d pairs', ind_code, n, pair_count)

                pair_gen = generate_all_pairs(dates_sorted)

                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures_map = {}
                    batch = []
                    processed_pairs = 0

                    for date_from, date_to in pair_gen:
                        fut = executor.submit(_fetch_range, reg, ind_code, date_from, date_to)
                        futures_map[fut] = (date_from, date_to)
                        batch.append(fut)

                        if len(batch) >= BATCH_SUBMIT:
                            for fut_done in as_completed(batch):
                                key, res = fut_done.result()
                                df, dt = futures_map[fut_done]
                                processed_pairs += 1

                                if isinstance(res, dict) and res.get('message'):
                                    logger.warning('Fetch error for %s %s..%s: %s', ind_code, df, dt,
                                                   res.get('message'))
                                    continue

                                if isinstance(res, list):
                                    payload_list = res
                                elif isinstance(res, dict):
                                    continue

                                params_pair = {
                                    'reg_number': reg,
                                    'ind_code': ind_code,
                                    'date_from': df,
                                    'date_to': dt,
                                }
                                try:
                                    created_or_updated, added, removed, canonical_obj = _update_or_create_bank_indicator_data_response(
                                            bank=bank_obj,
                                            form_type=form101_obj,
                                            params=params_pair,
                                            bank_indicator_obj=payload_list
                                    )
                                    logger.debug(f'Updated bank indicator data for form101 bank={bank_data["name"]}. '
                                                'Pair %s..%s saved: upd=%s added=%d removed=%d',
                                                df.isoformat(), dt.isoformat(), created_or_updated, len(added),
                                                len(removed))
                                except Exception as e:
                                    logger.exception('DB save error for %s %s..%s: %s', ind_code, df, dt, e)

                            batch = []

                    if batch:
                        for fut_done in as_completed(batch):
                            key, res = fut_done.result()
                            df, dt = futures_map[fut_done]
                            processed_pairs += 1

                            if isinstance(res, dict) and res.get('message'):
                                logger.warning('Fetch error for %s %s..%s: %s', ind_code, df, dt, res.get('message'))
                                continue

                            if isinstance(res, list):
                                payload_list = res
                            elif isinstance(res, dict):
                                continue

                            params_pair = {
                                'reg_number': reg,
                                'ind_code': ind_code,
                                'date_from': df,
                                'date_to': dt,
                            }
                            try:
                                created_or_updated, added, removed, canonical_obj = _update_or_create_bank_indicator_data_response(
                                        bank=bank_obj,
                                        form_type=form101_obj,
                                        params=params_pair,
                                        bank_indicator_obj=payload_list
                                )
                                logger.debug(f'Updated bank indicator data for form101 bank={bank_data["name"]}. '
                                            'Pair %s..%s saved: upd=%s added=%d removed=%d',
                                            df.isoformat(), dt.isoformat(), created_or_updated, len(added),
                                            len(removed))
                            except Exception as e:
                                logger.exception('DB save error for %s %s..%s: %s', ind_code, df, dt, e)

                logger.debug('Finished indicator %s: processed pairs=%d', ind_code, processed_pairs)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_all_bank_api_info(self):
    """
    Месячная задача:
    - обновляем денежно-кредитную статистику из REST парсера или
    - берём список банков и для каждого запускаем парсеры SOAP
    - сравниваем результаты с БД и обновляем только если поменялось
    :return: None
    """

    started = timezone.now()
    logger.info(f'[!] START update_all_bank_api_info at {started} [!]')

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

        logger.info(f"{'=' * 10} START PARSE 101, 123, 810 FORMS {'=' * 10}")

        def generate_f810_dates(start_year: int = 2000, end_year: int | None = None) -> list[str]:
            """
            Генерирует ISO-строки для дат 1 января и 1 апреля каждого года в диапазоне.
            Формат: "YYYY-MM-DDT00:00:00Z" (timezone-aware строка с Z).
            По умолчанию: с 2000 по текущий год (в часовом поясе Django).
            """
            if end_year is None:
                # берем текущий год в том часовом поясе, который использует Django
                end_year = timezone.now().year

            dates: list[str] = []
            for y in range(start_year, end_year + 1):
                dates.append(f"{y:04d}-01-01T00:00:00Z")
                dates.append(f"{y:04d}-04-01T00:00:00Z")
            return dates

        form810_obj = FormType.objects.get(title=form_f810()['title'])
        f810_dates_iso = generate_f810_dates()

        for dt in f810_dates_iso:
            parsed_dt = parse_datetime(dt)
            if parsed_dt is None:
                logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                continue
            if timezone.is_aware(parsed_dt):
                parsed_dt = parsed_dt.replace(tzinfo=None)

            bank_indicator_data = Form810Parser.parse(reg, parsed_dt)
            if 'message' in bank_indicator_data or not bank_indicator_data:
                logger.warning(
                        f'[!!] RETURN EMPTY bank indicator data for form810 and bank {bank_data["name"]}. '
                        f'STOP update bank indicator data. Message: {str(bank_indicator_data)} [!!]')
            else:
                created_or_updated, added, removed, canonical_obj = _update_or_create_bank_indicator_data_response(
                        bank=bank_obj,
                        form_type=form810_obj,
                        bank_indicator_obj=bank_indicator_data,
                        params={'reg_number': reg, 'dt': parsed_dt}
                )
                logger.debug(
                        "Saved F810 for bank %s dt=%s -> upd=%s added=%d removed=%d",
                        bank_data['name'], parsed_dt.isoformat(), created_or_updated,
                        len(added) if added is not None else 0,
                        len(removed) if removed is not None else 0
                )

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
            logger.debug(f'Updated datetimes for form123 and bank {bank_data["name"]} = {created_or_updated}'
                        f' Added = {added}, removed = {removed}')

            for dt in datetimes_data.get('datetimes', []):
                parsed_dt = parse_datetime(dt)
                if parsed_dt is None:
                    logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                    continue
                if timezone.is_aware(parsed_dt):
                    parsed_dt = parsed_dt.replace(tzinfo=None)
                indicators_data = Form123Parser.get_form123_indicators_from_data123(reg, parsed_dt)
                if 'message' in indicators_data or not indicators_data.get('indicators'):
                    logger.warning(f'[!!] RETURN EMPTY indicators for form123 and bank {bank_data["name"]}. '
                                   f'STOP update indicators. Message: {str(indicators_data)} [!!]')
                else:
                    created_or_updated, added, removed, indicators_data = _update_or_create_indicators_response(
                            bank=bank_obj, form_type=form123_obj, indicators_obj=indicators_data, params={
                                'reg_number': reg, 'dt': parsed_dt})
                    if not indicators_data:
                        continue
                    logger.debug(f'Updated indicators for form123 and bank {bank_data["name"]} = {created_or_updated}'
                                f' Added = {added}, removed = {removed}')

                    bank_indicator_data = Form123Parser.get_data123_form_full(reg, dt)
                    if 'message' in bank_indicator_data or not bank_indicator_data:
                        logger.warning(
                                f'[!!] RETURN EMPTY bank indicator data for form123 and bank {bank_data["name"]}. '
                                f'STOP update bank indicator data. Message: {str(bank_indicator_data)} [!!]')
                    else:
                        created_or_updated, added, removed, bank_indicator_data = (
                            _update_or_create_bank_indicator_data_response(bank=bank_obj, form_type=form123_obj,
                                                                           bank_indicator_obj=bank_indicator_data,
                                                                           params={'reg_number': reg, 'dt': parsed_dt}))
                        if not bank_indicator_data:
                            continue
                        logger.debug(
                                f'Updated bank indicator data for form123 and bank {bank_data["name"]} = {created_or_updated}'
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
            logger.debug(f'Updated datetimes for form101 and bank {bank_data["name"]} = {created_or_updated}'
                        f' Added = {added}, removed = {removed}')

            MAX_WORKERS = 10  # число потоков для параллельных запросов
            BATCH_SUBMIT = 300  # сколько задач отправлять в пул за раз

            indicators_map: dict[str, set[datetime] | list[datetime]] = {}
            unique_codes = set()
            for dt in datetimes_data.get('datetimes', []):
                parsed_dt = parse_datetime(dt)
                if parsed_dt is None:
                    logger.warning("Can't parse datetime %s for bank %s", parsed_dt, bank_obj.reg_number)
                    continue
                if timezone.is_aware(parsed_dt):
                    parsed_dt = parsed_dt.replace(tzinfo=None)
                indicators_data = Form101Parser.get_form101_indicators_from_data101(reg, parsed_dt)
                if 'message' in indicators_data or not indicators_data.get('indicators'):
                    logger.warning(f'[!!] RETURN EMPTY indicators for form101 and bank {bank_data["name"]}. '
                                   f'STOP update indicators. Message: {str(indicators_data)} [!!]')
                else:
                    for ind in indicators_data.get('indicators', []):
                        code = ind.get('ind_code')
                        if not code:
                            continue
                        if code not in unique_codes:
                            unique_codes.add(code)
                            indicators_map.setdefault(code, []).append(parsed_dt)

            def generate_all_pairs(dates_list):
                length = len(dates_list)
                for i in range(length):
                    di = dates_list[i]
                    for j in range(i, length):
                        yield di, dates_list[j]

            fetch_cache: dict[tuple, list] = {}

            def _fetch_range(bank_reg, ind_code_local, date_from, date_to):
                """
                Возвращает (key, payload) — key для кеша, payload: list|dict (если ошибка — dict с 'message').
                """
                key = (ind_code_local, date_from.isoformat(), date_to.isoformat())
                if key in fetch_cache:
                    return key, fetch_cache[key]
                try:
                    res = Form101Parser.get_indicator_data(reg_number=bank_reg,
                                                           ind_code=ind_code_local,
                                                           date_from=date_from,
                                                           date_to=date_to)
                except Exception as e:
                    res = {'message': f'exception: {e}'}
                fetch_cache[key] = res
                return key, res

            for ind_code, dates_sorted in indicators_map.items():
                if not dates_sorted:
                    continue

                dates_sorted = [i for i in dates_sorted if i.year >= 2018]

                n = len(dates_sorted)
                pair_count = n * (n + 1) // 2
                logger.debug('Indicator %s: %d dates -> %d pairs', ind_code, n, pair_count)

                pair_gen = generate_all_pairs(dates_sorted)

                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures_map = {}
                    batch = []
                    processed_pairs = 0

                    for date_from, date_to in pair_gen:
                        fut = executor.submit(_fetch_range, reg, ind_code, date_from, date_to)
                        futures_map[fut] = (date_from, date_to)
                        batch.append(fut)

                        if len(batch) >= BATCH_SUBMIT:
                            for fut_done in as_completed(batch):
                                key, res = fut_done.result()
                                df, dt = futures_map[fut_done]
                                processed_pairs += 1

                                if isinstance(res, dict) and res.get('message'):
                                    logger.warning('Fetch error for %s %s..%s: %s', ind_code, df, dt,
                                                   res.get('message'))
                                    continue

                                if isinstance(res, list):
                                    payload_list = res
                                elif isinstance(res, dict):
                                    continue

                                params_pair = {
                                    'reg_number': reg,
                                    'ind_code': ind_code,
                                    'date_from': df,
                                    'date_to': dt,
                                }
                                try:
                                    created_or_updated, added, removed, canonical_obj = _update_or_create_bank_indicator_data_response(
                                            bank=bank_obj,
                                            form_type=form101_obj,
                                            params=params_pair,
                                            bank_indicator_obj=payload_list
                                    )
                                    logger.debug(f'Updated bank indicator data for form101 bank={bank_data["name"]}. '
                                                'Pair %s..%s saved: upd=%s added=%d removed=%d',
                                                df.isoformat(), dt.isoformat(), created_or_updated, len(added),
                                                len(removed))
                                except Exception as e:
                                    logger.exception('DB save error for %s %s..%s: %s', ind_code, df, dt, e)

                            batch = []

                    if batch:
                        for fut_done in as_completed(batch):
                            key, res = fut_done.result()
                            df, dt = futures_map[fut_done]
                            processed_pairs += 1

                            if isinstance(res, dict) and res.get('message'):
                                logger.warning('Fetch error for %s %s..%s: %s', ind_code, df, dt, res.get('message'))
                                continue

                            if isinstance(res, list):
                                payload_list = res
                            elif isinstance(res, dict):
                                continue

                            params_pair = {
                                'reg_number': reg,
                                'ind_code': ind_code,
                                'date_from': df,
                                'date_to': dt,
                            }
                            try:
                                created_or_updated, added, removed, canonical_obj = _update_or_create_bank_indicator_data_response(
                                        bank=bank_obj,
                                        form_type=form101_obj,
                                        params=params_pair,
                                        bank_indicator_obj=payload_list
                                )
                                logger.debug(f'Updated bank indicator data for form101 bank={bank_data["name"]}. '
                                            'Pair %s..%s saved: upd=%s added=%d removed=%d',
                                            df.isoformat(), dt.isoformat(), created_or_updated, len(added),
                                            len(removed))
                            except Exception as e:
                                logger.exception('DB save error for %s %s..%s: %s', ind_code, df, dt, e)

                logger.debug('Finished indicator %s: processed pairs=%d', ind_code, processed_pairs)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_all_reports_api_info(self):
    """
    Месячная задача:
    Проходит по всем возможным комбинациям publication/dataset/measure (по ограничению в сериализаторах),
    сохраняет результаты проверки доступных параметров (params check) и затем создаёт/сохраняет
    реальные запросы по кредитам и депозитам, перебирая все подпериоды начиная с 2018 года
    (или начиная с минимально доступного года, если он > 2018).
    """
    CREDIT_PUBLICATIONS = {
        14: {'datasets': (25, 26, 27, 28, 29)},
        15: {'datasets': (30, 31, 32, 33, 34)},
        16: {'datasets': (35, 36)}
    }
    DEPOSIT_PUBLICATIONS = {
        18: {'datasets': (37, 38)},
        19: {'datasets': (39, 40)}
    }
    PUBLICATION_MEASURES = {
        14: (2, 3, 4),
        15: (23, 42, 55, 64, 72, 87, 95, 106),
        16: (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21),
        18: (2, 3, 4),
        19: (23, 42, 55, 64, 72, 87, 95, 106)
    }

    started = timezone.now()
    logger.info('[!] START update_all_reports_api_info at %s [!]', started)

    def _handle_params_check(publication_id=None, dataset_id=None, measure_id=None):
        """
        Выполняет check_available_params для переданных параметров.
        Создаёт/получает CbrApiDataRequest, но **сохраняет** CbrApiDataResponse ТОЛЬКО если
        ответ **валидный** (не содержит ключ 'message').
        Возвращает (req_obj, processed) где processed может быть None (если ответ невалидный).
        """
        params = {
            'publication_id': publication_id,
            'dataset_id': dataset_id,
            'measure_id': measure_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        logger.debug('Params-check called with %s', params)

        try:
            req = _create_or_get_request_atomic(CbrApiDataRequest.RateType.PARAMS_CHECK, params)
        except Exception as e:
            logger.exception('Failed to create/get params-check request for %s: %s', params, e)
            return None, None

        if hasattr(req, 'response') and req.response is not None:
            logger.debug('Existing params-check response found for %s', params)
            return req, req.response.processed_data

        try:
            data = CbrAPIParser.check_available_params(publication_id=publication_id,
                                                       dataset_id=dataset_id,
                                                       measure_id=measure_id)
        except Exception as e:
            logger.exception('check_available_params exception for %s: %s', params, e)
            return req, None

        if isinstance(data, dict) and data.get('message'):
            logger.warning('Params-check returned message for %s: %s', params, data.get('message'))
            return req, None

        try:
            if "publication_ids" in data:
                processed = CheckResponseSerializer(instance=data["publication_ids"], many=True).data
            elif "dataset_ids" in data:
                processed = CheckResponseSerializer(instance=data["dataset_ids"], many=True).data
            elif "measure_ids" in data:
                processed = CheckResponseSerializer(instance=data["measure_ids"], many=True).data
            elif "years" in data:
                years_raw = data.get("years")
                if (isinstance(years_raw, (list, tuple)) and len(years_raw) == 2 and
                        years_raw[0] is not None and years_raw[1] is not None):
                    processed = CheckYearsResponseSerializer(
                            instance={"years": [int(years_raw[0]), int(years_raw[1])]}).data
                else:
                    logger.warning('Params-check returned invalid years for %s: %s', params, years_raw)
                    return req, None
            else:
                logger.warning('Params-check returned unknown structure for %s: %s', params, data)
                return req, None
        except Exception as e:
            logger.exception('Failed to serialize params-check response for %s: %s', params, e)
            return req, None

        try:
            with transaction.atomic():
                req_locked = CbrApiDataRequest.objects.select_for_update().get(pk=req.pk)
                if hasattr(req_locked, 'response') and req_locked.response is not None:
                    logger.debug('Another worker saved params-check response for %s', params)
                    return req_locked, req_locked.response.processed_data
                CbrApiDataResponse.objects.create(request=req_locked, processed_data=processed)
                logger.debug('Saved params-check response for %s', params)
        except Exception:
            logger.exception('Failed to save params-check response for %s', params)

        return req, processed

    try:
        _handle_params_check()
    except Exception:
        logger.exception('Error while handling global params-check')

    publication_ids = set(PUBLICATION_MEASURES.keys()) | set(CREDIT_PUBLICATIONS.keys()) | set(
            DEPOSIT_PUBLICATIONS.keys())
    publication_ids = sorted(publication_ids)

    years_map = {}  # key: (pub, ds, measure) -> (from_year, to_year)

    for pub in publication_ids:
        try:
            _handle_params_check(publication_id=pub)
        except Exception:
            logger.exception('Error while handling params-check for publication %s', pub)

        datasets = []
        if pub in CREDIT_PUBLICATIONS:
            datasets = list(CREDIT_PUBLICATIONS[pub].get('datasets', []))
        if pub in DEPOSIT_PUBLICATIONS:
            datasets = list(DEPOSIT_PUBLICATIONS[pub].get('datasets', [])) or datasets

        for ds in datasets:
            try:
                _handle_params_check(publication_id=pub, dataset_id=ds)
            except Exception:
                logger.exception('Error params-check for pub=%s ds=%s', pub, ds)

            measures = PUBLICATION_MEASURES.get(pub, ())
            for m in measures:
                try:
                    req, processed = _handle_params_check(publication_id=pub, dataset_id=ds, measure_id=m)
                    # processed должен быть dict с ключом 'years' (после сериализации) либо None
                    if isinstance(processed, dict) and 'years' in processed:
                        yrs = processed['years']
                        try:
                            fy, ty = int(yrs[0]), int(yrs[1])
                            years_map[(pub, ds, m)] = (fy, ty)
                        except Exception:
                            logger.warning('Invalid years format for pub=%s ds=%s m=%s -> %s', pub, ds, m, yrs)
                except Exception:
                    logger.exception('Error params-check for pub=%s ds=%s measure=%s', pub, ds, m)

    def _generate_year_pairs(available_from: int, available_to: int, min_start: int = 2018):
        start = max(available_from, min_start)
        if start > available_to:
            return []
        pairs = []
        for fy in range(start, available_to + 1):
            for ty in range(fy, available_to + 1):
                pairs.append((fy, ty))
        return pairs

    # 3) Для кредитных публикаций — создаём/выполняем все подпериоды
    for pub, meta in CREDIT_PUBLICATIONS.items():
        datasets = meta.get('datasets', ())
        measures = PUBLICATION_MEASURES.get(pub, ())
        for ds in datasets:
            for m in measures:
                key = (pub, ds, m)
                years = years_map.get(key)
                if not years:
                    logger.warning('No years info for credit combo pub=%s ds=%s measure=%s, skipping', pub, ds, m)
                    continue
                avail_from, avail_to = years
                year_pairs = _generate_year_pairs(avail_from, avail_to, min_start=2018)
                logger.debug('CREDIT pub=%s ds=%s measure=%s -> %d year pairs (from %s to %s)',
                            pub, ds, m, len(year_pairs), avail_from, avail_to)

                for from_year, to_year in year_pairs:
                    params = {
                        'publication_id': pub,
                        'dataset_id': ds,
                        'measure_id': m,
                        'from_year': from_year,
                        'to_year': to_year,
                    }
                    try:
                        req_obj = _create_or_get_request_atomic(CbrApiDataRequest.RateType.CREDIT, params,
                                                                with_years=True)
                    except Exception:
                        logger.exception('Failed to create/get CREDIT request for %s', params)
                        continue

                    if hasattr(req_obj, 'response') and req_obj.response is not None:
                        continue

                    try:
                        data = CbrAPIParser.parse(publication_id=pub,
                                                  dataset_id=ds,
                                                  measure_id=m,
                                                  from_year=from_year,
                                                  to_year=to_year)
                    except Exception as e:
                        logger.exception('CbrAPIParser.parse exception for CREDIT %s: %s', params, e)
                        continue

                    if isinstance(data, dict) and data.get('message'):
                        logger.warning('CbrAPIParser.parse returned message for CREDIT %s: %s', params,
                                       data.get('message'))
                        continue

                    try:
                        processed = ResponseSerializer(instance=data).data
                    except Exception as e:
                        logger.exception('Failed to serialize CREDIT response for %s: %s', params, e)
                        continue

                    try:
                        with transaction.atomic():
                            req_locked = CbrApiDataRequest.objects.select_for_update().get(pk=req_obj.pk)
                            if hasattr(req_locked, 'response') and req_locked.response is not None:
                                continue
                            CbrApiDataResponse.objects.create(request=req_locked, processed_data=processed)
                            logger.debug('Saved CREDIT response for %s', params)
                    except Exception:
                        logger.exception('Failed to save CREDIT response for %s', params)

    # 4) Для депозитных публикаций — создаём/выполняем все подпериоды
    for pub, meta in DEPOSIT_PUBLICATIONS.items():
        datasets = meta.get('datasets', ())
        measures = PUBLICATION_MEASURES.get(pub, ())
        for ds in datasets:
            for m in measures:
                key = (pub, ds, m)
                years = years_map.get(key)
                if not years:
                    logger.warning('No years info for deposit combo pub=%s ds=%s measure=%s, skipping', pub, ds, m)
                    continue
                avail_from, avail_to = years
                year_pairs = _generate_year_pairs(avail_from, avail_to, min_start=2018)
                logger.debug('DEPOSIT pub=%s ds=%s measure=%s -> %d year pairs (from %s to %s)',
                            pub, ds, m, len(year_pairs), avail_from, avail_to)

                for from_year, to_year in year_pairs:
                    params = {
                        'publication_id': pub,
                        'dataset_id': ds,
                        'measure_id': m,
                        'from_year': from_year,
                        'to_year': to_year,
                    }
                    try:
                        req_obj = _create_or_get_request_atomic(CbrApiDataRequest.RateType.DEPOSIT, params,
                                                                with_years=True)
                    except Exception:
                        logger.exception('Failed to create/get DEPOSIT request for %s', params)
                        continue

                    if hasattr(req_obj, 'response') and req_obj.response is not None:
                        continue

                    try:
                        data = CbrAPIParser.parse(
                                publication_id=pub,
                                dataset_id=ds,
                                measure_id=m,
                                from_year=from_year,
                                to_year=to_year,
                        )
                    except Exception as e:
                        logger.exception('CbrAPIParser.parse exception for DEPOSIT %s: %s', params, e)
                        continue

                    if isinstance(data, dict) and data.get('message'):
                        logger.warning('CbrAPIParser.parse returned message for DEPOSIT %s: %s', params,
                                       data.get('message'))
                        continue

                    try:
                        processed = ResponseSerializer(instance=data).data
                    except Exception as e:
                        logger.exception('Failed to serialize DEPOSIT response for %s: %s', params, e)
                        continue

                    try:
                        with transaction.atomic():
                            req_locked = CbrApiDataRequest.objects.select_for_update().get(pk=req_obj.pk)
                            if hasattr(req_locked, 'response') and req_locked.response is not None:
                                continue
                            CbrApiDataResponse.objects.create(request=req_locked, processed_data=processed)
                            logger.debug('Saved DEPOSIT response for %s', params)
                    except Exception:
                        logger.exception('Failed to save DEPOSIT response for %s', params)

    logger.info('[!] FINISHED update_all_reports_api_info at %s [!]', timezone.now())
