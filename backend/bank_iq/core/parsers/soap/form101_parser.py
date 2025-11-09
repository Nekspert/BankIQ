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


class Form101Parser:
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
    def get_dates_for_f101(cls, reg_number: int) -> dict[str, list[datetime]] | dict[str, str]:
        if cls._client is None:
            cls._ensure_client()
        try:
            resp = cls._client.service.GetDatesForF101(CredprgNumber=reg_number)
            return {'datetimes': resp} if isinstance(resp, list) else {'message': f'Ошибка внешнего API: {str(resp)}'}

        except RequestException as e:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {e}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception('Ошибка получения дат для F101: %s', e)
            return {'message': f'Внутренняя ошибка: {str(e)}'}

    @classmethod
    def get_form101_indicators(cls) -> list[dict[str, Any]] | dict[str, str]:
        if cls._client is None:
            cls._ensure_client()
        try:
            resp = cls._client.service.Form101IndicatorsEnum()
            if not hasattr(resp, 'schema') or not hasattr(resp, '_value_1'):
                logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {resp}')
                return {'message': f'Ошибка внешнего API: {str(resp)}'}
            resp = serialize_object(resp._value_1)
            if isinstance(resp, dict):
                raw_items = resp['_value_1']
                result = []
                for item in raw_items:
                    if 'EIND' in item:
                        eind = item['EIND']
                        ind_data = {
                            'IndID': eind.get('IndID', ''),
                            'IndCode': eind.get('IndCode', ''),
                            'name': eind.get('name', ''),
                            'IndType': eind.get('IndType', ''),
                            'IndChapter': eind.get('IndChapter', ''),
                        }
                        result.append(ind_data)
                return result
            return {'message': f'Ошибка внешнего API: {str(resp)}'}

        except RequestException as e:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {e}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception('Ошибка получения индикаторов F101: %s', e)
            return {'message': f'Внутренняя ошибка: {e}'}

    @classmethod
    def get_indicator_data(cls, reg_number: int, ind_code: str,
                           date_from: datetime, date_to: datetime) -> list[dict] | dict[str, str]:
        """Получает данные для одного индикатора (IndCode)"""
        if cls._client is None:
            cls._ensure_client()
        try:
            resp = cls._client.service.Data101FullV2(
                    CredorgNumber=reg_number,
                    IndCode=ind_code,
                    DateFrom=date_from,
                    DateTo=date_to
            )
            res: list[dict] = cls._parse_data101_resp(resp, reg_number)
            if res is None:
                logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {res}')
                return {'message': f'Ошибка внешнего API: {str(res)}'}
            return res

        except RequestException as e:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {e}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception(f'Unexpected error in get_all_banks: {e}')
            return {'message': f'Внутренняя ошибка: {str(e)}'}

    @staticmethod
    def _parse_data101_resp(resp: Any, reg_number: int) -> list[dict] | None:
        try:
            resp_serial = serialize_object(resp)
            if '_value_1' in resp_serial and isinstance(resp_serial['_value_1'], dict) and '_value_1' in resp_serial[
                '_value_1']:
                raw_items = resp_serial['_value_1']['_value_1']
                result: list[dict] = []
                for item in raw_items:
                    if 'FDF' in item:
                        data = item['FDF']
                        result.append(dict(
                                bank_reg_number=str(reg_number),
                                date=data.get('dt'),
                                pln=data.get('pln', ''),
                                ap=int(data.get('ap', 0)),
                                vitg=float(data.get('vitg', 0)),
                                iitg=float(data.get('iitg', 0))
                        ))
                return result
            return None
        except Exception as e:
            logger.exception('Ошибка парсинга Data101Form: %s', e)
            return None

    @classmethod
    def get_data101_new(cls, reg_number: int, dt: datetime) -> dict:
        if cls._client is None:
            cls._ensure_client()
        try:
            resp = cls._client.service.Data101FNew(CredorgNumber=reg_number, dt=dt)
            resp_serial = serialize_object(resp)
            return resp_serial

        except RequestException as e:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {e}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception(f'Unexpected error in get_all_banks: {e}')
            return {'message': f'Внутренняя ошибка: {str(e)}'}

    @classmethod
    def get_form101_indicators_from_data101(cls, reg_number: int, date: datetime) -> dict[str, list] | dict[str, str]:
        if cls._client is None:
            cls._ensure_client()
        resp_serial = cls.get_data101_new(reg_number, date)
        raw_items = None
        if isinstance(resp_serial, dict):
            if '_value_1' in resp_serial:
                inner = resp_serial['_value_1']
                if isinstance(inner, dict) and '_value_1' in inner:
                    raw_items = inner['_value_1']
                elif isinstance(inner, list):
                    raw_items = inner

        if raw_items is None or 'message' in resp_serial:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {resp_serial}')
            return {'message': f'Ошибка внешнего API: {resp_serial}'}

        found_ind_codes = set()
        for item in raw_items:
            f = item.get('F101') if isinstance(item, dict) else None
            if not f or not isinstance(f, dict):
                continue
            ind_code = f.get('numsc')
            if ind_code is None:
                continue

            if ind_code not in found_ind_codes:
                found_ind_codes.add(ind_code)

        result = []
        master = cls.get_form101_indicators()

        if isinstance(master, list) and master:
            master_map = {str(m.get('IndCode')): m for m in master}
            for ind_code in found_ind_codes:
                meta = master_map.get(ind_code)
                if meta:
                    result.append({
                        'name': meta.get('name'),
                        'ind_code': ind_code
                    })
            return {'indicators': result}
        return master
