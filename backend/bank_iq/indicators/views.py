import json
from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from banks.models import Bank
from core.helpers.indicators_db_functions import _create_or_get_bank_indicators_data_request_atomic, \
    _create_or_get_indicators_request_atomic, _find_existing_bank_indicators_data_request, \
    _find_existing_indicators_request
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from core.parsers.soap.form810_parser import Form810Parser
from .models import BankIndicatorDataResponse, BankIndicatorsResponse, FormType
from .serializers import BankIndicator101DataSerializer, BankIndicator101RequestSerializer, \
    BankIndicator123DataSerializer, BankIndicator810DataSerializer, Indicators101Serializer, Indicators123Serializer, \
    RegNumAndDatetimeSerializer


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
                500: OpenApiResponse(description='Ошибка сервера', )
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
                        response=BankIndicator101DataSerializer,
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
                ),
                500: OpenApiResponse(description='Ошибка сервера', )
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
                422: OpenApiResponse(description="Ошибка внешнего API или парсера."),
                500: OpenApiResponse(description='Ошибка сервера', )
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
                        response=BankIndicator123DataSerializer,
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
                422: OpenApiResponse(description="Ошибка внешнего API или парсера."),
                500: OpenApiResponse(description='Ошибка сервера', )
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


class BankIndicator810APIView(APIView):
    @extend_schema(
            summary="Значения индикаторов формы F810 для банка на дату",
            description=(
                    "Возвращает значения показателей формы F810 (структурированные данные о капитале и активах)"
                    " для заданного банка на указанную дату.\n\n"
                    "Вход (JSON): `{ \"reg_number\": <int>, \"dt\": \"<ISO-8601 datetime>\" }`.\n\n"
                    "Возвращаемая структура: массив объектов, каждый объект представляет строку формы — `{ \"NUM_STR\": ..., "
                    "\"LABEL\": ..., \"NUM_P\": ..., \"USTKAP\": ..., \"SOB_AK\": ..., \"EMIS_DOH\": ..., \"PER_CB\": ..., "
                    "\"PER_OS\": ..., \"DELTADVR\": ..., \"PER_IH\": ..., \"REZERVF\": ..., \"VKL_V_IM\": ..., \"NERASP_PU\": ..., "
                    "\"ITOGO_IK\": ... }`.\n\n"
                    "Описание полей (в каждом элементе массива):\n"
                    "- `NUM_STR` (float) — номер строки (например, 1.0, 5.1).\n"
                    "- `LABEL` (string) — описание/лейбл строки (например, 'Данные на начало предыдущего отчетного года').\n"
                    "- `NUM_P` (string) — дополнительный номер/пункт (может быть '-', '3.12, 5', '4.1.9' или числом).\n"
                    "- `USTKAP` (float) — уставный капитал.\n"
                    "- `SOB_AK` (float) — собственные акции.\n"
                    "- `EMIS_DOH` (float) — эмиссионный доход.\n"
                    "- `PER_CB` (float) — переоценка ценных бумаг.\n"
                    "- `PER_OS` (float) — переоценка основных средств.\n"
                    "- `DELTADVR` (float) — дельта ДВР (возможно, дельта добавочного капитала).\n"
                    "- `PER_IH` (float) — переоценка инструментов хеджирования.\n"
                    "- `REZERVF` (float) — резервный фонд.\n"
                    "- `VKL_V_IM` (float) — вклады в имущество.\n"
                    "- `NERASP_PU` (float) — нераспределенная прибыль (убыток).\n"
                    "- `ITOGO_IK` (float) — итого источники капитала.\n\n"
                    "Коды ответов:\n"
                    "- 200 — OK (массив значений)\n"
                    "- 400 — неверный формат запроса\n"
                    "- 422 — ошибка при обращении к внешнему SOAP-сервису или внутренняя ошибка\n\n"
                    "Примечание: `dt` в запросе обрабатывается как naive datetime — если был передан timezone-aware, "
                    "смещение будет отброшено при обработке."
            ),
            request=RegNumAndDatetimeSerializer,
            examples=[
                OpenApiExample(
                        name="Пример запроса",
                        value={
                            "reg_number": 2015,
                            "dt": "2019-01-01T00:00:00Z",
                        },
                        request_only=True,
                        media_type='application/json'
                )
            ],
            responses={
                200: OpenApiResponse(
                        response=BankIndicator810DataSerializer,
                        description="Успешный ответ — значения индикаторов F810",
                        examples=[
                            OpenApiExample(
                                    name="Пример успешного ответа",
                                    value=[
                                        {
                                            "NUM_STR": 1.0,
                                            "LABEL": "Данные на начало предыдущего отчетного года",
                                            "NUM_P": "",
                                            "USTKAP": 1000000000.0,
                                            "SOB_AK": 50000000.0,
                                            "EMIS_DOH": 200000000.0,
                                            "PER_CB": 150000000.0,
                                            "PER_OS": 300000000.0,
                                            "DELTADVR": 0.0,
                                            "PER_IH": 50000000.0,
                                            "REZERVF": 100000000.0,
                                            "VKL_V_IM": 0.0,
                                            "NERASP_PU": 400000000.0,
                                            "ITOGO_IK": 2200000000.0
                                        },
                                        {
                                            "NUM_STR": 2.0,
                                            "LABEL": "Данные на начало отчетного года",
                                            "NUM_P": "1.1",
                                            "USTKAP": 1100000000.0,
                                            "SOB_AK": 60000000.0,
                                            "EMIS_DOH": 250000000.0,
                                            "PER_CB": 200000000.0,
                                            "PER_OS": 350000000.0,
                                            "DELTADVR": 10000000.0,
                                            "PER_IH": 60000000.0,
                                            "REZERVF": 120000000.0,
                                            "VKL_V_IM": 50000000.0,
                                            "NERASP_PU": 450000000.0,
                                            "ITOGO_IK": 2550000000.0
                                        }
                                    ]
                            )
                        ]
                ),
                400: OpenApiResponse(
                        description="Ошибка валидации запроса.",
                        examples=[
                            OpenApiExample(
                                    name="Пример ошибки валидации",
                                    value={"reg_number": ["A valid integer is required."]}
                            ),
                        ],
                ),
                422: OpenApiResponse(
                        description="Ошибка внешнего API или парсера.",
                        examples=[
                            OpenApiExample(name="Ошибка внешнего API", value={"message": "Ошибка внешнего API: ..."}),
                            OpenApiExample(name="Внутренняя ошибка", value={"message": "Внутренняя ошибка: ..."})
                        ]
                ),
                500: OpenApiResponse(description='Ошибка сервера', )
            }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = RegNumAndDatetimeSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        params = in_serializer.validated_data
        bank = Bank.objects.get(reg_number=params['reg_number'])
        form_type = FormType.objects.get(title='F810')

        existing = _find_existing_bank_indicators_data_request(bank, form_type, **params)
        if existing and hasattr(existing, 'response'):
            return Response(existing.response.bank_indicator_data, status=status.HTTP_200_OK)

        data = Form810Parser.parse(params['reg_number'], params['dt'])
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        processed_data = BankIndicator810DataSerializer(instance=data, many=True).data
        req_obj = _create_or_get_bank_indicators_data_request_atomic(bank, form_type, **params)
        if hasattr(req_obj, 'response') and req_obj.response is not None:
            return Response(req_obj.response.bank_indicator_data, status=status.HTTP_200_OK)

        BankIndicatorDataResponse.objects.create(request=req_obj, bank_indicator_data=processed_data)
        return Response(processed_data, status=status.HTTP_200_OK)
