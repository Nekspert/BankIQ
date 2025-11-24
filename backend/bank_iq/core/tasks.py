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
from core.one_time_tasks import form_f101, form_f123, form_f810
from core.parsers.soap import all_banks_parser
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from core.parsers.soap.form810_parser import Form810Parser
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
                logger.info(
                        "Saved F810 for bank %s dt=%s -> upd=%s added=%d removed=%d",
                        reg, parsed_dt.isoformat(), created_or_updated, len(added) if added is not None else 0,
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
                if 'message' in indicators_data or not indicators_data.get('indicators'):
                    logger.warning(f'[!!] RETURN EMPTY indicators for form123 and bank {bank_data["name"]}. '
                                   f'STOP update indicators. Message: {str(indicators_data)} [!!]')
                else:
                    created_or_updated, added, removed, indicators_data = _update_or_create_indicators_response(
                            bank=bank_obj, form_type=form123_obj, indicators_obj=indicators_data, params={
                                'reg_number': reg, 'dt': parsed_dt})
                    if not indicators_data:
                        continue
                    logger.info(f'Updated indicators for form123 and bank {bank_data["name"]} = {created_or_updated}'
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
                        logger.info(
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
            logger.info(f'Updated datetimes for form101 and bank {bank_data["name"]} = {created_or_updated}'
                        f' Added = {added}, removed = {removed}')

            MAX_WORKERS = 10  # число потоков для параллельных запросов
            BATCH_SUBMIT = 300  # сколько задач отправлять в пул за раз

            indicators_map: dict[str, set[datetime] | list[datetime]] = {}
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
                        indicators_map.setdefault(code, set()).add(parsed_dt)

            for code in list(indicators_map.keys()):
                indicators_map[code] = sorted(indicators_map[code])

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

                n = len(dates_sorted)
                pair_count = n * (n + 1) // 2
                logger.info('Indicator %s: %d dates -> %d pairs', ind_code, n, pair_count)

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
                                    logger.info(f'Updated bank indicator data for form101 bank={bank_data["name"]}. '
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
                                logger.info(f'Updated bank indicator data for form101 bank={bank_data["name"]}. '
                                            'Pair %s..%s saved: upd=%s added=%d removed=%d',
                                            df.isoformat(), dt.isoformat(), created_or_updated, len(added),
                                            len(removed))
                            except Exception as e:
                                logger.exception('DB save error for %s %s..%s: %s', ind_code, df, dt, e)

                logger.info('Finished indicator %s: processed pairs=%d', ind_code, processed_pairs)
