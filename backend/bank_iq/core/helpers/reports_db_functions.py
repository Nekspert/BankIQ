from django.db import IntegrityError, transaction

from reports.models import CbrApiDataRequest


def _find_existing_request(rate_type: str, params: dict, with_years: bool = False) -> CbrApiDataRequest:
    q = CbrApiDataRequest.objects.filter(
            rate_type=rate_type,
            publication_id=params.get('publication_id'),
            dataset_id=params.get('dataset_id'),
            measure_id=params.get('measure_id'),
    )
    if with_years:
        q = q.filter(from_year=params.get('from_year'), to_year=params.get('to_year'))
    return q.select_related('response').first()


def _create_or_get_request_atomic(rate_type: str, params: dict, with_years: bool = False) -> CbrApiDataRequest:
    defaults = {}
    if with_years:
        defaults.update({
            'from_year': params.get('from_year'),
            'to_year': params.get('to_year'),
        })
    try:
        with transaction.atomic():
            obj, created = CbrApiDataRequest.objects.get_or_create(
                    rate_type=rate_type,
                    publication_id=params.get('publication_id'),
                    dataset_id=params.get('dataset_id'),
                    measure_id=params.get('measure_id'),
                    defaults=defaults
            )
    except IntegrityError:
        obj = _find_existing_request(rate_type, params, with_years=with_years)
    return obj
