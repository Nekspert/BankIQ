import logging
from types import SimpleNamespace

import requests
from requests.exceptions import RequestException


logger = logging.getLogger(__name__)


class CBRParser:
    BASE_URL = 'http://www.cbr.ru/dataservice'
    REQUEST_TIMEOUT = 5

    @classmethod
    def check_available_params(cls,
                               publication_id: int | None = None,
                               dataset_id: int | None = None,
                               measure_id: int | None = None) -> dict:
        logger.info('check_available_params called with '
                    f'publication_id={publication_id}, dataset_id={dataset_id}, measure_id={measure_id}')
        res: list[dict] = []
        try:
            session = requests.Session()

            if publication_id is None:
                resp = session.get(f"{cls.BASE_URL}/publications", timeout=cls.REQUEST_TIMEOUT)
                resp.raise_for_status()
                publications = resp.json(object_hook=lambda d: SimpleNamespace(**d))
                if not publications:
                    return {'message': 'Не удалось получить доступные публикации от API'}
                for obj in publications:
                    pid = getattr(obj, 'id', None)
                    title = getattr(obj, 'category_name', None)
                    noactive = getattr(obj, 'NoActive', None)
                    res.append({'id': pid,
                                'title': title,
                                'status': 'column [non-searchable]' if noactive else 'value [searchable]'})
                return {'publication_ids': res}

            if dataset_id is None:
                resp = session.get(f"{cls.BASE_URL}/datasets", params={'publicationId': publication_id},
                                   timeout=cls.REQUEST_TIMEOUT)
                resp.raise_for_status()
                datasets = resp.json(object_hook=lambda d: SimpleNamespace(**d))
                if not datasets:
                    return {'message': 'Не удалось получить доступные датасеты от API'}
                for obj in datasets:
                    did = getattr(obj, 'id', None)
                    name = getattr(obj, 'name', None)
                    res.append({'id': did, 'title': name, 'status': 'value [searchable]'})
                return {'dataset_ids': res}

            if measure_id is None:
                resp = session.get(f"{cls.BASE_URL}/measures", params={'datasetId': dataset_id},
                                   timeout=cls.REQUEST_TIMEOUT)
                resp.raise_for_status()
                measures = resp.json(object_hook=lambda d: SimpleNamespace(**d)).measure
                if not measures:
                    return {'message': 'Не удалось получить доступные разрезы (measures) от API'}
                for obj in measures:
                    mid = getattr(obj, 'id', None)
                    name = getattr(obj, 'name', None)
                    res.append({'id': mid, 'title': name, 'status': 'value [searchable]'})
                return {'measure_ids': res}

            params = {'measureId': measure_id, 'datasetId': dataset_id}
            resp = session.get(f"{cls.BASE_URL}/years", params=params, timeout=cls.REQUEST_TIMEOUT)
            resp.raise_for_status()
            years_data = resp.json(object_hook=lambda d: SimpleNamespace(**d))
            if not years_data:
                return {'message': 'Не удалось получить доступные годы от API'}
            years = years_data[0]
            return {'years': [years.FromYear, years.ToYear]}

        except RequestException as e:
            logger.error(f'Ошибка при запросе к API ЦБ РФ: {str(e)}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception('Unexpected error in check_available_params')
            return {'message': f'Внутренняя ошибка: {str(e)}'}

    @classmethod
    def parse(cls, publication_id: int, dataset_id: int, measure_id: int, from_year: int, to_year: int) -> dict:
        logger.info('parse called with '
                    f'publication_id={publication_id}, dataset_id={dataset_id}, '
                    f'measure_id={measure_id}, from_year={from_year}, to_year={to_year}')
        try:
            session = requests.Session()

            years_params = {'measureId': measure_id, 'datasetId': dataset_id}
            resp_years = session.get(f"{cls.BASE_URL}/years", params=years_params, timeout=cls.REQUEST_TIMEOUT)
            resp_years.raise_for_status()
            years_data = resp_years.json(object_hook=lambda d: SimpleNamespace(**d))
            if not years_data:
                return {'message': 'Не удалось получить доступные годы от API'}
            years = years_data[0]
            if from_year < years.FromYear or to_year > years.ToYear:
                return {'message': f'Информация доступна только с {years.FromYear} по {years.ToYear} год'}
            payload = {
                'y1': from_year,
                'y2': to_year,
                'publicationId': publication_id,
                'datasetId': dataset_id,
                'measureId': measure_id
            }
            resp_data = session.get(f'{cls.BASE_URL}/data', params=payload, timeout=cls.REQUEST_TIMEOUT)
            resp_data.raise_for_status()
            data = resp_data.json()
            if not data or not data.get('RawData'):
                return {'message': 'Нет данных для указанных параметров'}
            return data
        except RequestException as e:
            logger.error(f'Ошибка при запросе к API ЦБ РФ: {str(e)}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
        except Exception as e:
            logger.exception('Unexpected error in parse')
            return {'message': f'Внутренняя ошибка: {str(e)}'}
