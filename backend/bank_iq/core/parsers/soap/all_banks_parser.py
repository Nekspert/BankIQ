import logging
import re
import xml.etree.ElementTree as ET
from typing import Any, Optional

import requests
import zeep
from lxml.etree import iselement
from lxml.html import tostring
from requests.exceptions import RequestException
from zeep import Settings
from zeep.transports import Transport


logger = logging.getLogger(__name__)


class CbrAllBanksParser:
    """
    Парсер списка всех банков ЦБ РФ.

    Стиль ответов:
      - При внешней ошибке возвращаем {'message': f'Ошибка внешнего API: ...'}
      - При внутренней ошибке возвращаем {'message': f'Внутренняя ошибка: ...'}
      - В успешном случае возвращаем {'banks': [{..bank..}, ... ]}
    """
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

    @staticmethod
    def _get_xml_str(response: Any) -> str:
        """Получение XML строки из ответа zeep"""
        try:
            if iselement(response):
                return tostring(response, encoding='unicode')
            if hasattr(response, 'text') and isinstance(response.text, str):
                return response.text
            return str(response)
        except Exception as e:
            logger.debug('Не удалось получить xml string: %s', e)
            return str(response)

    @staticmethod
    def _strip_namespaces(xml: str) -> str:
        """Удаление неймспейсов из XML для простого парсинга элементарными средствами"""
        if not xml:
            return ""
        # Удаляем декларации xmlns
        xml = re.sub(r'\sxmlns(:[A-Za-z0-9]+)?="[^"]*"', '', xml)
        # Удаляем префиксы у тегов
        xml = re.sub(r'</?([A-Za-z0-9]+):([A-Za-z0-9_]+)', r'<\2', xml)
        return xml

    @classmethod
    def _parse_enum_bic_xml(cls, xml_input: Any) -> list[dict]:
        """Парсит EnumBIC_XML и возвращает список словарей с полями из XML"""
        xml_str = cls._get_xml_str(xml_input)
        if not xml_str:
            return []

        try:
            xml_str = cls._strip_namespaces(xml_str)
            root = ET.fromstring(xml_str)
            result: list[dict] = []
            for bic_elem in root.findall('.//BIC'):
                if list(bic_elem):
                    bic_data = {}
                    for child in bic_elem:
                        tag = child.tag
                        text = child.text.strip() if child.text else ""
                        bic_data[tag] = text
                    if bic_data:
                        result.append(bic_data)
            return result
        except Exception as e:
            logger.exception('Ошибка парсинга EnumBIC_XML: %s', e)
            return []

    @staticmethod
    def _convert_to_dict(bank_data: dict) -> dict:
        """Преобразует словарь, полученный из XML, в определённую структуру"""
        return {
            'bic': bank_data.get('BIC', ''),
            'name': bank_data.get('NM', ''),
            'reg_number': int(bank_data.get('RN', 0)),
            'internal_code': bank_data.get('intCode', ''),
            'registration_date': bank_data.get('RC', ''),
            'region_code': bank_data.get('cregnr', ''),
            'tax_id': bank_data.get('RB', ''),
        }

    @classmethod
    def parse(cls) -> dict:
        """
        Возвращает словарь в формате:
            {'banks': [{bic:..., name:..., ...}, ... ]}
        В случае ошибки возвращает {'message': '...'} (соответственно статус код в view решает вызывающий)
        """
        try:
            cls._ensure_client()
            resp = cls._client.service.EnumBIC_XML()
            raw = cls._parse_enum_bic_xml(resp)

            return {'banks': [cls._convert_to_dict(item) for item in raw]}

        except RequestException as e:
            logger.error(f'Ошибка при запросе к внешнему API ЦБ РФ: {e}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception(f'Unexpected error in get_all_banks: {e}')
            return {'message': f'Внутренняя ошибка: {str(e)}'}
