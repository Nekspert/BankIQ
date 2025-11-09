import logging
from datetime import datetime
from typing import Any, Optional

import requests
import zeep
from requests import RequestException
from zeep import Settings
from zeep.helpers import serialize_object
from zeep.transports import Transport


logger = logging.getLogger(__name__)


class Form123Parser:
    WSDL_URL = 'https://www.cbr.ru/CreditInfoWebServ/CreditOrgInfo.asmx?WSDL'
    REQUEST_TIMEOUT = 5
    _client: Optional[zeep.Client] = None

    @classmethod
    def _ensure_client(cls):
        if cls._client is not None:
            return
        session = requests.Session()
        session.verify = True
        transport = Transport(session=session, timeout=cls.REQUEST_TIMEOUT)
        settings = Settings(strict=False)
        cls._client = zeep.Client(wsdl=cls.WSDL_URL, transport=transport, settings=settings)

    @classmethod
    def get_dates_for_f123(cls, reg_number: int) -> dict[str, list[datetime]] | dict[str, str]:
        if cls._client is None:
            cls._ensure_client()
        try:
            resp = cls._client.service.GetDatesForF123(CredprgNumber=reg_number)
            return {'datetimes': resp} if isinstance(resp, list) else {'message': f'Ошибка внешнего API: {str(resp)}'}
        except RequestException as e:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {e}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception('Ошибка получения дат для F123: %s', e)
            return {'message': f'Внутренняя ошибка: {str(e)}'}

    @classmethod
    def get_data123_form_full(cls, reg_number: int, on_date: datetime) -> list[dict] | dict[str, str]:
        if cls._client is None:
            cls._ensure_client()
        try:
            resp = cls._client.service.Data123FormFull(CredorgNumber=reg_number, OnDate=on_date)
            res = cls._parse_data123_resp(resp, reg_number)
            if res is None:
                logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {resp}')
                return {'message': f'Ошибка внешнего API: {str(resp)}'}
            return res
        except RequestException as e:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {e}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception(f'Unexpected error in get_data123_form_full: {e}')
            return {'message': f'Внутренняя ошибка: {str(e)}'}

    @staticmethod
    def _parse_data123_resp(resp: Any, reg_number: int) -> list[dict] | None:
        try:
            resp_serial = serialize_object(resp)
            if '_value_1' in resp_serial and isinstance(resp_serial['_value_1'], dict) and '_value_1' in resp_serial[
                '_value_1']:
                raw_items = resp_serial['_value_1']['_value_1']
                result = []
                for item in raw_items:
                    if 'F123' in item:
                        name = item['F123']['NAME']
                        if name not in ('Собственные средства (капитал), итого, в том числе:',
                                        'Базовый капитал, итого', 'Дополнительный капитал, итого'):
                            continue
                        result.append({'bank_reg_number': reg_number,
                                       'name': item['F123']['NAME'],
                                       'value': float(item['F123'].get('VALUE', 0))})
                if 'Собственные средства (капитал), итого, в том числе:' not in result:
                    result.append({'bank_reg_number': reg_number,
                                   'name': 'Собственные средства (капитал), итого, в том числе:',
                                   'value': 0.0})
                if 'Базовый капитал, итого' not in result:
                    result.append({'bank_reg_number': reg_number,
                                   'name': 'Базовый капитал, итого',
                                   'value': 0.0})
                if 'Дополнительный капитал, итого' not in result:
                    result.append({'bank_reg_number': reg_number,
                                   'name': 'Дополнительный капитал, итого',
                                   'value': 0.0})

                return result
            return None
        except Exception as e:
            logger.exception('Ошибка парсинга Data123FormFull: %s', e)
            return None

    @classmethod
    def get_form123_indicators_from_data123(cls, reg_number: int, date: datetime) -> dict[str, list] | dict[str, str]:
        if cls._client is None:
            cls._ensure_client()
        resp_serial = cls.get_data123_form_full(reg_number, date)
        if resp_serial is None or 'message' in resp_serial:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {resp_serial}')
            return {'message': f'Ошибка внешнего API: {resp_serial}'}
        result = []
        items = resp_serial
        for i in items:
            result.append({'name': i['name']})
        return {'indicators': result}
