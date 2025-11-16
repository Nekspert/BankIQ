import json
from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.helpers.indicators_db_functions import _create_banks_from_api, \
    _create_or_get_bank_indicators_data_request_atomic, _create_or_get_datetimes_request_atomic, \
    _create_or_get_indicators_request_atomic, _find_existing_bank_indicators_data_request, _find_existing_dates_request, \
    _find_existing_indicators_request, _get_all_banks_from_db
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from .models import Bank, BankDatesResponse, BankIndicatorDataResponse, BankIndicatorsResponse, FormType
from .serializers import AllBanksSerializer, BankIndicator101DataSerializer, BankIndicator101RequestSerializer, \
    BankIndicator123DataSerializer, DateTimesSerializer, Indicators101Serializer, Indicators123Serializer, \
    RegNumAndDatetimeSerializer, \
    RegNumberSerializer


class AllBanksAPIView(APIView):
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
                )
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
                )
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


class Indicators101APIView(APIView):
    @extend_schema(
            summary="Список доступных индикаторов формы F101 для банка",
            description=(
                    "Возвращает список индикаторов (показателей) формы F101, которые реально заполнены "
                    "для заданного банка на указанную дату.\n\n"
                    "Входные поля (JSON):\n"
                    "- `reg_number` (integer) — регистрационный номер банка в БД ЦБ РФ.\n"
                    "- `dt` (datetime, ISO-8601) — метка даты для которой требуется список индикаторов.\n\n"
                    "Возвращаемая структура: `{ \"indicators\": [ { \"name\": ..., \"ind_code\": ... }, ... ] }`.\n"
                    "Примечание: `dt` в запросе обрабатывается как naive datetime — если был передан timezone-aware, "
                    "смещение будет отброшено при обработке."
            ),
            examples=[OpenApiExample(
                    name="Пример запроса",
                    value={
                        "reg_number": 1481,
                        "dt": "2024-07-01T00:00:00Z"
                    },
                    request_only=True,
                    media_type='application/json'
            )],
            request=RegNumAndDatetimeSerializer,
            responses={
                200: OpenApiResponse(
                        response=Indicators101Serializer,
                        description="Успешный ответ — список доступных индикаторов",
                        examples=[
                            OpenApiExample(
                                    name="Пример успешного ответа",
                                    value={
                                        "indicators": [
                                            {
                                                "name": "Депозиты Федерального казначейства",
                                                "ind_code": "410"
                                            },
                                            {
                                                "name": "Корреспондентские счета",
                                                "ind_code": "301"
                                            },
                                            {
                                                "name": "Средства бюджетов субъектов Российской Федерации и местных бюджетов",
                                                "ind_code": "402"
                                            }
                                        ]
                                    }
                            )
                        ]
                ),
                400: OpenApiResponse(
                        description="Ошибка валидации входного запроса (RegNumAndDatetimeSerializer).",
                        examples=[
                            OpenApiExample(
                                    name="Пример ошибки валидации",
                                    value={"reg_number": ["A valid integer is required."]}
                            ),
                        ],
                ),
                422: OpenApiResponse(
                        description="Ошибка получения данных от внешнего SOAP-сервиса или внутренняя ошибка парсера.",
                        examples=[
                            OpenApiExample(name="Ошибка внешнего API",
                                           value={"message": "Ошибка внешнего API: <описание ошибки>"}),
                            OpenApiExample(name="Внутренняя ошибка",
                                           value={"message": "Внутренняя ошибка: <описание ошибки>"}),
                        ],
                ),
            },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = RegNumAndDatetimeSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        params = in_serializer.validated_data

        bank = Bank.objects.get(reg_number=params['reg_number'])
        form_type = FormType.objects.get(title='F101')
        existing = _find_existing_indicators_request(bank, form_type, params)
        if existing and hasattr(existing, 'response'):
            return Response(existing.response.indicators, status=status.HTTP_200_OK)

        data = Form101Parser.get_form101_indicators_from_data101(params['reg_number'], params['dt'])
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        processed_data = Indicators101Serializer(instance=data).data
        req_obj = _create_or_get_indicators_request_atomic(bank, form_type, params)
        if hasattr(req_obj, 'response') and req_obj.response is not None:
            return Response(req_obj.response.indicators, status=status.HTTP_200_OK)

        BankIndicatorsResponse.objects.create(request=req_obj, indicators=processed_data)
        return Response(processed_data, status=status.HTTP_200_OK)


class BankIndicator101APIView(APIView):
    @extend_schema(
            summary="Данные одного индикатора формы F101 для банка",
            description=(
                    "Возвращает значения указанного индикатора (IndCode) для банка в заданном диапазоне дат.\n\n"
                    "Входные параметры (JSON, request body):\n"
                    "- `reg_number` (integer) — регистрационный номер банка.\n"
                    "- `ind_code` (string) — код индикатора (numsc / IndCode).\n"
                    "- `date_from` (datetime, ISO-8601) — начало диапазона (включительно).\n"
                    "- `date_to` (datetime, ISO-8601) — конец диапазона (включительно).\n\n"
                    "Формат дат: ожидается naive datetime в теле запроса.\n\n"
                    "Возвращаемые поля (в каждом элементе массива):\n"
                    "- `bank_reg_number` (string) — регистрационный номер банка.\n"
                    "- `date` (datetime) — дата записи (поле dt/DT в исходной форме F101).\n"
                    "    - Описание `date`: это отчетная дата — обычно первый день месяца.\n"
                    "- `pln` (string) — глава плана счетов:\n"
                    "    - 'А' — балансовые счета; 'Б' — счета доверительного управления; 'В' — внебалансовые счета; "
                    "'Г' — срочные операции; 'Д' — счета Депо.\n"
                    "- `ap` (integer) — признак стороны: 1 — актив (A_P = '1'), 2 — пассив (A_P = '2').\n"
                    "- `vitg` (float) — входящие остатки (VITG) — итого, тыс. руб.\n"
                    "- `iitg` (float) — исходящие остатки (IITG) — итого, тыс. руб.\n\n"
            ),
            request=BankIndicator101RequestSerializer,
            examples=[
                OpenApiExample(
                        name="Пример запроса",
                        value={
                            "reg_number": 1481,
                            "ind_code": "410",
                            "date_from": "2024-06-01T00:00:00Z",
                            "date_to": "2024-07-01T00:00:00Z"
                        },
                        request_only=True,
                        media_type='application/json'
                )
            ],
            responses={
                200: OpenApiResponse(
                        response=BankIndicator101DataSerializer(many=True),
                        description="Успешный ответ — массив данных индикатора",
                        examples=[
                            OpenApiExample(
                                    name="Пример успешного ответа",
                                    value=[
                                        {
                                            "bank_reg_number": "1481",
                                            "date": "2024-06-01T00:00:00",
                                            "pln": "А",
                                            "ap": 2,
                                            "vitg": 15000000.0,
                                            "iitg": 18000000.0
                                        },
                                        {
                                            "bank_reg_number": "1481",
                                            "date": "2024-07-01T00:00:00",
                                            "pln": "А",
                                            "ap": 2,
                                            "vitg": 18000000.0,
                                            "iitg": 22000000.0
                                        }
                                    ]
                            )
                        ]
                ),
                400: OpenApiResponse(
                        description="Неверный запрос (валидация входных данных)."
                ),
                422: OpenApiResponse(
                        description="Ошибка при обращении к внешнему SOAP-сервису или внутренняя ошибка парсера.",
                        examples=[
                            OpenApiExample(name="Ошибка внешнего API", value={"message": "Ошибка внешнего API: ..."}),
                            OpenApiExample(name="Внутренняя ошибка", value={"message": "Внутренняя ошибка: ..."})
                        ]
                )
            }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = BankIndicator101RequestSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        params = in_serializer.validated_data

        bank = Bank.objects.get(reg_number=params['reg_number'])
        form_type = FormType.objects.get(title='F101')
        existing = _find_existing_bank_indicators_data_request(bank, form_type, **params)
        if existing and hasattr(existing, 'response'):
            return Response(existing.response.bank_indicator_data, status=status.HTTP_200_OK)

        data: list[dict] = Form101Parser.get_indicator_data(**params)
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        processed_data = BankIndicator101DataSerializer(instance=data, many=True).data
        req_obj = _create_or_get_bank_indicators_data_request_atomic(bank, form_type, **params)
        if hasattr(req_obj, 'response') and req_obj.response is not None:
            return Response(req_obj.response.bank_indicator_data, status=status.HTTP_200_OK)

        BankIndicatorDataResponse.objects.create(request=req_obj, bank_indicator_data=processed_data)
        return Response(processed_data, status=status.HTTP_200_OK)


class UniqueIndicators101APIView(APIView):
    @extend_schema(
            summary="Список уникальных индикаторов формы F101",
            description=(
                    "Возвращает список уникальных индикаторов (catalog) формы F101.\n\n"
                    "Данные загружаются из локального JSON-файла `api_payloads/unique_indicators_clean.json`.\n\n"
                    "Структура ответа (200): `{ \"indicators\": [ { \"ind_code\": ..., \"name\": ... }, ... ] }`.\n\n"
                    "Если файл невалиден или при чтении произошла ошибка — возвращается статус 500 с описанием."
            ),
            responses={
                200: OpenApiResponse(
                        response=Indicators101Serializer,
                        description="Успешный ответ — объект с полем `indicators` (список индикаторов).",
                        examples=[
                            OpenApiExample(
                                    name="Пример ответа — несколько индикаторов",
                                    value={
                                        "indicators": [
                                            {"ind_code": "303", "name": "Внутрибанковские требования и обязательства"},
                                            {"ind_code": "410", "name": "Депозиты Федерального казначейства"},
                                            {"ind_code": "963", "name": "Обязательства по поставке денежных средств"}
                                        ]
                                    }
                            )
                        ]
                ),
                500: OpenApiResponse(
                        description="Ошибка при чтении или декодировании локального JSON-файла.",
                        examples=[
                            OpenApiExample(name="Invalid JSON file", value={"message": "Invalid JSON file"}),
                            OpenApiExample(name="IO / other error", value={"detail": "<описание ошибки>"})
                        ]
                )
            }
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        try:
            path = Path(settings.BASE_DIR) / 'api_payloads' / 'unique_indicators_clean.json'
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return Response({'message': 'Invalid JSON file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        out_serializer = Indicators101Serializer(instance=data)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class Datetimes123APIView(APIView):
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
                )
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


class Indicators123APIView(APIView):
    @extend_schema(
            summary="Список доступных индикаторов формы F123 для банка",
            description=(
                    "Возвращает список индикаторов формы F123, которые заполнены "
                    "для заданного банка на указанную дату.\n\n"
                    "Вход (JSON): `{ \"reg_number\": <int>, \"dt\": \"<ISO-8601 datetime>\" }`.\n\n"
                    "Возвращаемая структура: `{ \"indicators\": [ { \"name\": ... }, ... ] }`.\n\n"
                    "Коды ответов:\n"
                    "- 200 — OK (список индикаторов)\n"
                    "- 400 — неверный формат запроса (валидатор)\n"
                    "- 422 — ошибка при обращении к внешнему SOAP-сервису или внутренняя ошибка парсера"
            ),
            request=RegNumAndDatetimeSerializer,
            examples=[
                OpenApiExample(
                        name="Пример запроса",
                        value={
                            "reg_number": 1481,
                            "dt": "2024-06-01T00:00:00Z",
                        },
                        request_only=True,
                        media_type='application/json'
                )
            ],
            responses={
                200: OpenApiResponse(
                        response=Indicators123Serializer,
                        description="Список доступных индикаторов F123."
                ),
                400: OpenApiResponse(description="Ошибка валидации запроса."),
                422: OpenApiResponse(description="Ошибка внешнего API или парсера.")
            }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = RegNumAndDatetimeSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        params = in_serializer.validated_data
        bank = Bank.objects.get(reg_number=params['reg_number'])
        form_type = FormType.objects.get(title='F123')

        existing = _find_existing_indicators_request(bank, form_type, params)
        if existing and hasattr(existing, 'response'):
            return Response(existing.response.indicators, status=status.HTTP_200_OK)

        data = Form123Parser.get_form123_indicators_from_data123(params['reg_number'], params['dt'])
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        processed_data = Indicators123Serializer(instance=data).data

        req_obj = _create_or_get_indicators_request_atomic(bank, form_type, params)
        if hasattr(req_obj, 'response') and req_obj.response is not None:
            return Response(req_obj.response.indicators, status=status.HTTP_200_OK)

        BankIndicatorsResponse.objects.create(request=req_obj, indicators=processed_data)
        return Response(processed_data, status=status.HTTP_200_OK)


class BankIndicator123APIView(APIView):
    @extend_schema(
            summary="Значения индикаторов формы F123 для банка на дату",
            description=(
                    "Возвращает значения показателей формы F123 (name/value) для заданного банка на указанную дату.\n\n"
                    "Вход (JSON): `{ \"reg_number\": <int>, \"dt\": \"<ISO-8601 datetime>\" }`.\n\n"
                    "Возвращаемая структура: массив объектов, каждый объект — `{ \"bank_reg_number\": ...,"
                    " \"name\": ..., \"value\": ... }`.\n\n"
                    "Коды ответов:\n"
                    "- 200 — OK (массив значений)\n"
                    "- 400 — неверный формат запроса\n"
                    "- 422 — ошибка при обращении к внешнему SOAP-сервису или внутренняя ошибка"
            ),
            request=RegNumAndDatetimeSerializer,
            examples=[
                OpenApiExample(
                        name="Пример запроса",
                        value={
                            "reg_number": 1481,
                            "dt": "2024-06-01T00:00:00Z",
                        },
                        request_only=True,
                        media_type='application/json'
                )
            ],
            responses={
                200: OpenApiResponse(
                        response=BankIndicator123DataSerializer(many=True),
                        description="Успешный ответ — значения индикаторов F123",
                        examples=[
                            OpenApiExample(
                                    name="Пример успешного ответа",
                                    value=[
                                        {
                                            "bank_reg_number": "1481",
                                            "name": "Собственные средства (капитал), итого, в том числе:",
                                            "value": 6500000000.0
                                        },
                                        {
                                            "bank_reg_number": "1481",
                                            "name": "Базовый капитал, итого",
                                            "value": 5500000000.0
                                        },
                                        {
                                            "bank_reg_number": "1481",
                                            "name": "Дополнительный капитал, итого",
                                            "value": 1000000000.0
                                        }
                                    ]
                            )
                        ]
                ),
                400: OpenApiResponse(description="Ошибка валидации запроса."),
                422: OpenApiResponse(description="Ошибка внешнего API или парсера.")
            }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = RegNumAndDatetimeSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        params = in_serializer.validated_data
        bank = Bank.objects.get(reg_number=params['reg_number'])
        form_type = FormType.objects.get(title='F123')

        existing = _find_existing_bank_indicators_data_request(bank, form_type, **params)
        if existing and hasattr(existing, 'response'):
            return Response(existing.response.bank_indicator_data, status=status.HTTP_200_OK)

        data = Form123Parser.get_data123_form_full(params['reg_number'], params['dt'])
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        processed_data = BankIndicator123DataSerializer(instance=data, many=True).data
        req_obj = _create_or_get_bank_indicators_data_request_atomic(bank, form_type, **params)
        if hasattr(req_obj, 'response') and req_obj.response is not None:
            return Response(req_obj.response.bank_indicator_data, status=status.HTTP_200_OK)

        BankIndicatorDataResponse.objects.create(request=req_obj, bank_indicator_data=processed_data)
        return Response(processed_data, status=status.HTTP_200_OK)
