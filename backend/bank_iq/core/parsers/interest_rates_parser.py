from types import SimpleNamespace

import requests
from requests import RequestException


class InterestRatesCreditParser:
    """
    Введите id публикации:
    id:14 title:В целом по Российской Федерации
    id:15 title:В территориальном разрезе
    id:16 title:В разрезе по видам экономической деятельности

    Введите id показателя:
    id:25, title:Ставки по кредитам нефинансовым организациям
    id:26, title:Ставки по кредитам нефинансовым организациям-субъектам МСП
    id:27, title:Ставки по кредитам физическим лицам
    id:28, title:Ставки по автокредитам
    id:29, title:Ставки по ипотечным жилищным кредитам

    Введите id разреза:
    id:2, title:В рублях
    id:3, title:В долларах США
    id:4, title:В евро

    Введите год начала периода:2014  # example
    Введите год окончания периода:2025  # example
    """
    BASE_URL = 'http://www.cbr.ru/dataservice'

    @classmethod
    def parse(cls, publication_id: int, dataset_id: int, measure_id: int, from_year: int, to_year: int) -> dict:
        cls.publication_id = publication_id
        cls.dataset_id = dataset_id
        cls.measure_id = measure_id
        cls.from_year = from_year
        cls.to_year = to_year

        years_params = {'measureId': cls.measure_id, 'datasetId': cls.dataset_id}
        try:
            response_years = requests.get(f"{cls.BASE_URL}/years", params=years_params)
            response_years.raise_for_status()
            years = response_years.json(object_hook=lambda d: SimpleNamespace(**d))[0]
            if cls.from_year < years.FromYear or cls.to_year > years.ToYear:
                return {'message': f'Информация доступна только с {years.FromYear} по {years.ToYear} год'}

            payload = {
                'y1': cls.from_year,
                'y2': cls.to_year,
                'publicationId': cls.publication_id,
                'datasetId': cls.dataset_id,
                "measureId": cls.measure_id
            }
            response_data = requests.get(f"{cls.BASE_URL}/data", params=payload)
            response_data.raise_for_status()
            return response_data.json()
        except RequestException as e:
            return {"message": f"Ошибка внешнего API: {str(e)}"}
