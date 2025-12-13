from banks.models import Bank, BankDatesResponse
from banks.serializers import DateTimesSerializer
from core.helpers.indicators_db_functions import _create_or_get_datetimes_request_atomic
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from indicators.models import FormType


def get_datetimes_period(datetimes: dict) -> list[str | None]:
    try:
        datetimes_list = datetimes['datetimes']
    except KeyError:
        return [None, None]
    if not datetimes_list:
        return [None, None]
    start = datetimes_list[0]
    end = datetimes_list[-1]
    return [start, end]


def get_datetimes(params: dict, form_type: FormType, bank: Bank) -> dict[str, str | list]:
    if form_type.title == "F101":
        data = Form101Parser.get_dates_for_f101(params['reg_number'])
    else:
        data = Form123Parser.get_dates_for_f123(params['reg_number'])

    if 'message' in data:
        return data

    processed_data = DateTimesSerializer(instance=data).data
    req_obj = _create_or_get_datetimes_request_atomic(bank, form_type, params)

    if hasattr(req_obj, 'response') and req_obj.response is not None:
        datetimes101 = req_obj.response.datetimes
    else:
        datetimes101 = processed_data
    BankDatesResponse.objects.create(request=req_obj, datetimes=processed_data)
    return datetimes101
