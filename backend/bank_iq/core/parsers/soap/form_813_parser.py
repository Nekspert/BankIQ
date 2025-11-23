import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import zeep
from lxml.etree import iselement
from lxml.html import tostring
from requests.exceptions import RequestException
from zeep import Settings
from zeep.transports import Transport

from core.parsers.soap.all_banks_parser import CbrAllBanksParser


logger = logging.getLogger(__name__)


class CbrF813MParser:
    WSDL_URL = 'https://www.cbr.ru/CreditInfoWebServ/CreditOrgInfo.asmx?WSDL'
    REQUEST_TIMEOUT = 10
    _client: Optional[zeep.Client] = None

    @classmethod
    def _ensure_client(cls) -> None:
        if cls._client is not None:
            return
        session = requests.Session()
        session.verify = True
        transport = Transport(session=session, timeout=cls.REQUEST_TIMEOUT)
        settings = Settings(strict=False)
        cls._client = zeep.Client(wsdl=cls.WSDL_URL, transport=transport, settings=settings)

    @staticmethod
    def _get_xml_str(response: Any) -> str:
        try:
            if iselement(response):
                return tostring(response, encoding='unicode')
            if hasattr(response, 'text') and isinstance(response.text, str):
                return response.text
            return str(response)
        except Exception as e:
            logger.debug("Не удалось получить xml string: %s", e)
            return str(response)

    @staticmethod
    def _strip_namespaces(xml: str) -> str:
        if not xml:
            return ""
        xml = re.sub(r'\sxmlns(:[A-Za-z0-9]+)?="[^"]*"', '', xml)
        xml = re.sub(r'</?([A-Za-z0-9]+):([A-Za-z0-9_]+)', r'<\2', xml)
        return xml

    @staticmethod
    def _local_name(tag: str) -> str:
        if not tag:
            return ''
        if tag.startswith('{'):
            return tag.split('}', 1)[1]
        return tag

    @staticmethod
    def _to_number_if_possible(value: Optional[str]) -> Any:
        if value is None:
            return None
        s = value.strip()
        if s == "":
            return ""
        if re.fullmatch(r'-?\d+(?:\.\d+)?', s):
            try:
                return float(s)
            except Exception:
                return s
        return s

    @classmethod
    def _parse_f813m_rows_from_xml(cls, xml_input: Any) -> Dict[str, Any]:
        xml_str = cls._get_xml_str(xml_input)
        if not xml_str:
            return {'on_date': None, 'rows': []}
        xml_str = cls._strip_namespaces(xml_str)
        try:
            root = ET.fromstring(xml_str)
        except Exception as e:
            logger.debug("Первичный парсинг XML не удался: %s", e)
            try:
                root = ET.fromstring(cls._get_xml_str(xml_input))
            except Exception as e2:
                logger.exception("Ошибка финального парсинга XML: %s", e2)
                return {'on_date': None, 'rows': []}
        docs_elem = root.find('.//Docs')
        if docs_elem is None:
            for el in root.iter():
                if cls._local_name(el.tag) == 'Docs':
                    docs_elem = el
                    break
        on_date = docs_elem.get('OnDate') if docs_elem is not None else None
        rows_parsed: List[Dict[str, Any]] = []
        if docs_elem is not None:
            f813m = None
            for child in docs_elem:
                if cls._local_name(child.tag) == 'f813m':
                    f813m = child
                    break
            row_elems = []
            if f813m is not None:
                for child in f813m:
                    if cls._local_name(child.tag) == 'row':
                        row_elems.append(child)
            else:
                for el in docs_elem.iter():
                    if cls._local_name(el.tag) == 'row':
                        row_elems.append(el)
            for row in row_elems:
                attrs = {}
                for k, v in row.attrib.items():
                    attrs[k] = cls._to_number_if_possible(v)
                rows_parsed.append(attrs)
        return {'on_date': on_date, 'rows': rows_parsed}

    @classmethod
    def parse(cls, credorg_number: int, date_time: datetime, par: int) -> dict:
        try:
            cls._ensure_client()
            resp = cls._client.service.GetF813MXml(
                    CredorgNumber=credorg_number,
                    dateTime=date_time,
                    par=par
            )
            result = cls._parse_f813m_rows_from_xml(resp)
            return result
        except RequestException as e:
            logger.error("Ошибка при запросе к внешнему API ЦБ РФ: %s", e)
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception("Unexpected error in GetF813MXml: %s", e)
            return {'message': f'Внутренняя ошибка: {str(e)}'}


if __name__ == '__main__':
    banks = CbrAllBanksParser.parse()
    for bank in banks['banks']:
        credorg_number = bank['reg_number']
        name = bank['name']
        print(name, credorg_number)
        for datet in [datetime(2019, 1, 1), datetime(2019, 1, 31)]:
            for pr in [1, 2, 3, 4]:
                parsed = CbrF813MParser.parse(credorg_number, datet, 1)
                print("on_date:", parsed.get('on_date'), "par:", pr, "rows count:", len(parsed.get('rows', [])))
                if parsed.get('rows'):
                    for row in parsed['rows']:
                        print(row)
                print()
