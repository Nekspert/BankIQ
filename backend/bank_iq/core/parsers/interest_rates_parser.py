import logging
from types import SimpleNamespace

import requests
from requests.exceptions import RequestException


logger = logging.getLogger(__name__)


class InterestRatesParser:
    BASE_URL = 'http://www.cbr.ru/dataservice'

    @classmethod
    def parse(cls, publication_id: int, dataset_id: int, measure_id: int, from_year: int, to_year: int) -> dict:
        cls.publication_id = publication_id
        cls.dataset_id = dataset_id
        cls.measure_id = measure_id
        cls.from_year = from_year
        cls.to_year = to_year

        logger.info('requested params: '
                    f'publication_id = {cls.publication_id}'
                    f'dataset_id = {cls.dataset_id}'
                    f'measure_id = {cls.measure_id}'
                    f'from_year = {cls.from_year}'
                    f'to_year = {cls.to_year}')

        years_params = {'measureId': cls.measure_id, 'datasetId': cls.dataset_id}
        try:
            response_years = requests.get(f"{cls.BASE_URL}/years", params=years_params)
            response_years.raise_for_status()
            years_data = response_years.json(object_hook=lambda d: SimpleNamespace(**d))
            if not years_data:
                return {'message': 'Не удалось получить доступные годы от API'}
            years = years_data[0]
            if cls.from_year < years.FromYear or cls.to_year > years.ToYear:
                return {'message': f'Информация доступна только с {years.FromYear} по {years.ToYear} год'}

            payload = {
                'y1': cls.from_year,
                'y2': cls.to_year,
                'publicationId': cls.publication_id,
                'datasetId': cls.dataset_id,
                "measureId": cls.measure_id
            }
            response_data = requests.get(f'{cls.BASE_URL}/data', params=payload)
            response_data.raise_for_status()
            data = response_data.json()
            if not data.get('RawData'):
                return {'message': 'Нет данных для указанных параметров'}
            return data
        except RequestException as e:
            logger.error(f'Ошибка при запросе к API ЦБ РФ: {str(e)}')
            return {'message': f'Ошибка внешнего API: {str(e)}'}
