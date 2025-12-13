from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.helpers.indicators_db_functions import _create_banks_from_api, \
    _create_or_get_datetimes_request_atomic, _find_existing_dates_request, _get_all_banks_from_db
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from core.utils.datetimes_period import get_datetimes, get_datetimes_period
from indicators.models import FormType
from .models import Bank, BankDatesResponse
from .serializers import AllBanksSerializer, BankProfileSerializer, DateTimesSerializer, \
    RegNumberSerializer


class AllBanksAPIView(APIView):
    authentication_classes = []

    @extend_schema(
            summary="Список всех банков (справочник BIC) от ЦБ РФ",
            description=(
                    "Возвращает справочник банков, получаемый из SOAP-сервиса ЦБ РФ (метод EnumBIC_XML).\n\n"
                    "Каждая запись в поле `banks` содержит основную справочную информацию об организации.\n\n"
                    "Примечания по полям:\n"
                    "- `bic` — банковский идентификатор (строка, обязателен).\n"
                    "- `reg_number` — регистрационный номер в базе ЦБ (число).\n"
                    "- `registration_date` — дата регистрации; может содержать смещение часового пояса.\n\n"
                    "Возвращаемый код: 200 — OK; 422 — ошибка при обращении к внешнему SOAP-сервису или внутренняя "
                    "ошибка парсера."
            ),
            responses={
                200: OpenApiResponse(
                        response=AllBanksSerializer,
                        description="Успешный ответ — объект со списком банков в поле `banks`.",
                        examples=[
                            OpenApiExample(
                                    name="Пример ответа — несколько банков",
                                    value={
                                        "banks": [
                                            {
                                                "bic": "040173745",
                                                "name": "СИБСОЦБАНК",
                                                "reg_number": 2015,
                                                "internal_code": "10000012",
                                                "registration_date": "1992-08-21T00:00:00+04:00",
                                                "region_code": "1022200525819",
                                                "tax_id": "1022200525819"
                                            },
                                            {
                                                "bic": "044525225",
                                                "name": "ПАО СБЕРБАНК",
                                                "reg_number": 1234,
                                                "internal_code": "20000001",
                                                "registration_date": "1990-01-01T00:00:00+03:00",
                                                "region_code": "7700000000000",
                                                "tax_id": "7700000000"
                                            }
                                        ]
                                    }
                            )
                        ]
                ),
                422: OpenApiResponse(
                        description="Ошибка получения данных от внешнего SOAP-сервиса или внутренняя ошибка.",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка внешнего API",
                                    value={"message": "Ошибка внешнего API: <описание ошибки>"}
                            ),
                            OpenApiExample(
                                    name="Внутренняя ошибка",
                                    value={"message": "Внутренняя ошибка: <описание ошибки>"}
                            )
                        ]
                ),
                500: OpenApiResponse(description='Ошибка сервера', )
            }
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        data = _get_all_banks_from_db()

        if data is None:
            data = _create_banks_from_api()
            if 'message' in data:
                return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        out_serializer = AllBanksSerializer(instance=data)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class Datetimes101APIView(APIView):
    authentication_classes = []

    @extend_schema(
            summary="Список доступных дат формы F101 для банка",
            description=(
                    "Возвращает список дат (меток времени), для которых у банка доступна форма F101 в сервисе ЦБ "
                    "РФ.\n\n Входной параметр: JSON `{ \"reg_number\": <int> }`.\n\n"
                    "Формат и часовой пояс: возвращаемые даты представлены в ISO-8601.\n"
                    "Если используется aware-datetime, в ответе они будут конвертированы в UTC (Z).\n\n"
                    "Пример запроса: `{ \"reg_number\": 1481 }`.\n"
            ),
            request=RegNumberSerializer,
            examples=[
                OpenApiExample(
                        name="Пример запроса",
                        value={'reg_number': 1481},
                        media_type='application/json')
            ],
            responses={
                200: OpenApiResponse(
                        response=DateTimesSerializer,
                        description="Успешный ответ — доступные даты формы F101",
                        examples=[
                            OpenApiExample(
                                    name="Пример успешного ответа",
                                    value={
                                        "datetimes": [
                                            "2024-01-01T00:00:00Z",
                                            "2024-02-01T00:00:00Z",
                                            "2024-03-01T00:00:00Z"
                                        ]
                                    }
                            )
                        ]
                ),
                400: OpenApiResponse(
                        description="Неверный запрос",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка валидации",
                                    value={
                                        "reg_number": ["Обязательное поле."]
                                    }
                            )
                        ]
                ),
                422: OpenApiResponse(
                        description="Ошибка получения данных",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка внешнего API",
                                    value={
                                        "message": "Ошибка внешнего API: Банк с указанным регистрационным номером не найден"
                                    }
                            )
                        ]
                ),
                500: OpenApiResponse(description='Ошибка сервера', )
            }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = RegNumberSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        params = in_serializer.validated_data

        bank = Bank.objects.get(reg_number=params['reg_number'])
        form_type = FormType.objects.get(title='F101')
        existing = _find_existing_dates_request(bank, form_type, params)

        if existing and hasattr(existing, 'response'):
            return Response(existing.response.datetimes, status=status.HTTP_200_OK)

        data = Form101Parser.get_dates_for_f101(params['reg_number'])
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        processed_data = DateTimesSerializer(instance=data).data
        req_obj = _create_or_get_datetimes_request_atomic(bank, form_type, params)

        if hasattr(req_obj, 'response') and req_obj.response is not None:
            return Response(req_obj.response.datetimes, status=status.HTTP_200_OK)

        BankDatesResponse.objects.create(request=req_obj, datetimes=processed_data)
        return Response(processed_data, status=status.HTTP_200_OK)


class Datetimes123APIView(APIView):
    authentication_classes = []

    @extend_schema(
            summary="Список доступных дат формы F123 для банка",
            description=(
                    "Возвращает список дат (меток времени), для которых у банка доступна форма F123 в сервисе ЦБ "
                    "РФ.\n\n Входной параметр: JSON `{ \"reg_number\": <int> }`.\n\n"
                    "Формат и часовой пояс: возвращаемые даты представлены в ISO-8601.\n"
                    "Если используется aware-datetime, в ответе они будут конвертированы в UTC (Z).\n\n"
                    "Пример запроса: `{ \"reg_number\": 1481 }`.\n"
            ),
            request=RegNumberSerializer,
            examples=[
                OpenApiExample(
                        name="Пример запроса",
                        value={'reg_number': 1481},
                        media_type='application/json')
            ],
            responses={
                200: OpenApiResponse(
                        response=DateTimesSerializer,
                        description="Успешный ответ — доступные даты формы F123.",
                        examples=[
                            OpenApiExample(
                                    name="Успешный ответ — пример",
                                    value={
                                        "datetimes": [
                                            "2023-10-01T00:00:00+00:00",
                                            "2023-11-01T00:00:00+00:00"
                                        ]
                                    }
                            )
                        ]
                ),
                422: OpenApiResponse(
                        description="Ошибка получения данных от внешнего SOAP-сервиса или внутренняя ошибка.",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка внешнего API",
                                    value={"message": "Ошибка внешнего API: <описание ошибки>"}
                            ),
                            OpenApiExample(
                                    name="Внутренняя ошибка",
                                    value={"message": "Внутренняя ошибка: <описание ошибки>"}
                            ),
                        ]
                ),
                400: OpenApiResponse(
                        description="Неверный запрос: тело не соответствует RegNumberSerializer.",
                        examples=[
                            OpenApiExample(
                                    name="Пример ошибки валидации",
                                    value={"reg_number": ["A valid integer is required."]}
                            )
                        ]
                ),
                500: OpenApiResponse(description='Ошибка сервера', )
            }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = RegNumberSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        params = in_serializer.validated_data
        bank = Bank.objects.get(reg_number=params['reg_number'])
        form_type = FormType.objects.get(title='F123')

        existing = _find_existing_dates_request(bank, form_type, params)
        if existing and hasattr(existing, 'response'):
            return Response(existing.response.datetimes, status=status.HTTP_200_OK)

        data = Form123Parser.get_dates_for_f123(params['reg_number'])
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        processed_data = DateTimesSerializer(instance=data).data
        req_obj = _create_or_get_datetimes_request_atomic(bank, form_type, params)

        if hasattr(req_obj, 'response') and req_obj.response is not None:
            return Response(req_obj.response.datetimes, status=status.HTTP_200_OK)

        BankDatesResponse.objects.create(request=req_obj, datetimes=processed_data)
        return Response(processed_data, status=status.HTTP_200_OK)


class BankProfileApiView(APIView):
    authentication_classes = []

    @extend_schema(
            summary="Профиль банка с диапазонами доступных дат для форм F101 и F123",
            description=(
                    "Возвращает подробный профиль банка по его регистрационному номеру, включая основную справочную информацию "
                    "и диапазоны доступных дат (начальная и конечная даты) для форм F101 и F123 из сервиса ЦБ РФ.\n\n"
                    "Этот эндпоинт принимает один параметр в пути URL:\n"
                    "- `reg_number`: Регистрационный номер банка в базе ЦБ РФ (целое число, обязателен). "
                    "Это уникальный идентификатор банка для запроса его профиля. Пример: 1481.\n\n"
                    "В ответе возвращается объект с информацией о банке и диапазонами дат. Диапазоны представляют собой списки из двух элементов: "
                    "[начальная дата, конечная дата] в формате ISO-8601 в UTC. Если для формы нет доступных дат, "
                    "соответствующий список будет пустым ([]).\n\n"
                    "Возвращаемые поля:\n"
                    "- `bic`: БИК банка (Bank Identification Code). Уникальный идентификатор банка (строка, обязателен). Пример: '044525225'.\n"
                    "- `name`: Полное наименование кредитной организации (строка, обязателен).\n"
                    "- `reg_number`: Регистрационный номер организации в базе ЦБ РФ (целое число, обязателен). Пример: 1481.\n"
                    "- `internal_code`: Внутренний код/идентификатор банка в источнике данных (если доступен) (строка, обязателен).\n"
                    "- `registration_date`: Дата регистрации организации (ISO 8601). Может содержать смещение часового пояса (дата-время, обязателен).\n"
                    "- `region_code`: Код региона (региональный номер/код) (строка, обязателен).\n"
                    "- `tax_id`: Идентификатор налогоплательщика (ИНН) или другой налоговый идентификатор, если присутствует (строка, обязателен).\n"
                    "- `start_and_end_101`: Диапазон доступных дат для формы F101 (список из двух дат в ISO-8601 или пустой список). "
                    "Первая дата — самая ранняя доступная, вторая — самая поздняя.\n"
                    "- `start_and_end_123`: Диапазон доступных дат для формы F123 (список из двух дат в ISO-8601 или пустой список). "
                    "Первая дата — самая ранняя доступная, вторая — самая поздняя.\n\n"
                    "Возвращаемые коды: 200 — OK; 404 — банк не найден; 422 — ошибка при обращении к внешнему сервису; "
                    "500 — внутренняя ошибка сервера."
            ),
            responses={
                200: OpenApiResponse(
                        response=BankProfileSerializer,
                        description="Успешный ответ — профиль банка с диапазонами дат.",
                        examples=[
                            OpenApiExample(
                                    name="Пример ответа для банка",
                                    value={
                                        "bic": "044525225",
                                        "name": "ПАО СБЕРБАНК",
                                        "reg_number": 1481,
                                        "internal_code": "20000001",
                                        "registration_date": "1991-06-20T00:00:00Z",
                                        "region_code": "7700000000000",
                                        "tax_id": "7707083893",
                                        "start_and_end_101": ["2020-01-01T00:00:00Z", "2024-12-01T00:00:00Z"],
                                        "start_and_end_123": ["2021-01-01T00:00:00Z", "2024-11-01T00:00:00Z"]
                                    }
                            ),
                            OpenApiExample(
                                    name="Пример с пустыми диапазонами",
                                    value={
                                        "bic": "040173745",
                                        "name": "СИБСОЦБАНК",
                                        "reg_number": 2015,
                                        "internal_code": "10000012",
                                        "registration_date": "1992-08-21T00:00:00Z",
                                        "region_code": "1022200525819",
                                        "tax_id": "1022200525819",
                                        "start_and_end_101": [],
                                        "start_and_end_123": []
                                    }
                            )
                        ]
                ),
                422: OpenApiResponse(
                        description="Ошибка получения данных от внешнего SOAP-сервиса или внутренняя ошибка парсера.",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка внешнего API",
                                    value={"message": "Ошибка внешнего API: <описание ошибки>"}
                            )
                        ]
                ),
                500: OpenApiResponse(
                        description="Внутренняя ошибка сервера"
                )
            }
    )
    def get(self, request: Request, reg_number: int, *args, **kwargs) -> Response:
        bank = Bank.objects.get(reg_number=reg_number)
        form_type101 = FormType.objects.get(title='F101')
        form_type123 = FormType.objects.get(title='F123')
        params = {'reg_number': reg_number}

        existing_101_datetimes = _find_existing_dates_request(bank=bank,
                                                              form_type=form_type101,
                                                              params=params)
        existing_123_datetimes = _find_existing_dates_request(bank=bank,
                                                              form_type=form_type123,
                                                              params=params)

        if existing_101_datetimes and hasattr(existing_101_datetimes, 'response'):
            datetimes101 = existing_101_datetimes.response.datetimes
        else:
            datetimes101 = get_datetimes(params=params, form_type=form_type101, bank=bank)

        if existing_123_datetimes and hasattr(existing_123_datetimes, 'response'):
            datetimes123 = existing_123_datetimes.response.datetimes
        else:
            datetimes123 = get_datetimes(params=params, form_type=form_type123, bank=bank)

        if 'message' in datetimes101 or 'message' in datetimes123:
            return Response({
                'datetimes101': datetimes101,
                'datetimes123': datetimes123}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        start_and_end_101 = get_datetimes_period(datetimes101)
        start_and_end_123 = get_datetimes_period(datetimes123)

        out_serializer = BankProfileSerializer(instance={'bic': bank.bic,
                                                         'name': bank.name,
                                                         'reg_number': bank.reg_number,
                                                         'internal_code': bank.internal_code,
                                                         'registration_date': bank.registration_date,
                                                         'region_code': bank.region_code,
                                                         'tax_id': bank.tax_id,
                                                         'start_and_end_101': start_and_end_101,
                                                         'start_and_end_123': start_and_end_123})
        return Response(out_serializer.data, status=status.HTTP_200_OK)
