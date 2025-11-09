import json
from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.parsers.soap.all_banks_parser import CbrAllBanksParser
from core.parsers.soap.form101_parser import Form101Parser
from .serializers import AllBanksSerializer, BankIndicatorDataSerializer, BankIndicatorRequestSerializer, \
    DateTimesSerializer, IndicatorsSerializer, \
    RegNumAndDatetimeSerializer, \
    RegNumberSerializer, UniqueIndicatorsSerializer


class AllBanksAPIView(APIView):
    @extend_schema(
            summary="Список всех банков (справочник BIC) от ЦБ РФ",
            description=(
                    "Эндпоинт возвращает список всех банков, доступных через SOAP-сервис ЦБ РФ (метод EnumBIC_XML). "
                    "Возвращаемая структура: объект с полем `banks`, содержащим массив банков."
                    "Каждая запись банка содержит фиксированный набор полей: "
                    "`bic`, `name`, `reg_number`, `internal_code`, `registration_date`, `region_code`, `tax_id`."
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
                                                "reg_number": "2015",
                                                "internal_code": "10000012",
                                                "registration_date": "1992-08-21T00:00:00+04:00",
                                                "region_code": "1022200525819",
                                                "tax_id": "1022200525819"
                                            },
                                            {
                                                "bic": "044525225",
                                                "name": "ПАО СБЕРБАНК",
                                                "reg_number": "1234",
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
        data = CbrAllBanksParser.parse()

        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        out_serializer = AllBanksSerializer(instance=data)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class DatetimesAPIView(APIView):
    @extend_schema(
            summary="Список доступных дат формы F101 для банка",
            description=(
                    "Возвращает список дат (меток времени), для которых у банка доступна "
                    "форма F101 в сервисе ЦБ РФ. Запрос — JSON объект с полем `reg_number`.\n\n"
                    "Пример запроса: `{ \"reg_number\": 1481 }`. Ответ: `{ \"datetimes\": [\"YYYY-MM-DDTHH:MM:SSZ\", "
                    "...] }`."
            ),
            request=RegNumberSerializer,
            responses={
                200: OpenApiResponse(
                        response=DateTimesSerializer,
                        description="Успешный ответ — доступные даты формы F101.",
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
        reg_number = in_serializer.validated_data['reg_number']

        data = Form101Parser.get_dates_for_f101(reg_number)
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        out_serializer = DateTimesSerializer(instance=data)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class IndicatorsAPIView(APIView):
    @extend_schema(
            summary="Список доступных индикаторов формы F101 для банка",
            description=(
                    "Возвращает список индикаторов (показателей) формы F101, которые реально заполнены "
                    "для заданного банка на указанную дату. Запрос — JSON-объект с двумя полями:\n\n"
                    "- `reg_number` (integer) — регистрационный номер банка в БД ЦБ РФ;\n"
                    "- `dt` (datetime) — метка даты (ISO-8601) для получения формы F101.\n\n"
                    "Если парсер вернул ошибку — возвращается статус 422 и объект `{'message': '...'}'."
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
                        response=IndicatorsSerializer,
                        description="Успешный ответ — объект с полем `indicators` (список индикаторов).",
                        examples=[
                            OpenApiExample(
                                    name="Успешный ответ — пример",
                                    value={
                                        "indicators": [
                                            {
                                                "name": "Депозиты Федерального казначейства",
                                                "ind_code": "410",
                                                "ind_id": 410,
                                                "ind_type": "1",
                                                "ind_chapter": "A"
                                            },
                                            {
                                                "name": "Обязательства по поставке денежных средств",
                                                "ind_code": "963",
                                                "ind_id": 1593,
                                                "ind_type": "1",
                                                "ind_chapter": "Г"
                                            }
                                        ]
                                    }
                            )
                        ],
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
                            OpenApiExample(
                                    name="Ошибка внешнего API",
                                    value={"message": "Ошибка внешнего API: <описание ошибки>"}
                            ),
                            OpenApiExample(
                                    name="Внутренняя ошибка",
                                    value={"message": "Внутренняя ошибка: <описание ошибки>"}
                            ),
                        ],
                ),
            },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        in_serializer = RegNumAndDatetimeSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        reg_number = in_serializer.validated_data['reg_number']
        dt = in_serializer.validated_data['dt']

        data = Form101Parser.get_form101_indicators_from_data101(reg_number, dt)
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        out_serializer = IndicatorsSerializer(instance=data)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class BankIndicatorAPIView(APIView):
    @extend_schema(
            summary="Данные одного индикатора формы F101 для банка",
            description=(
                    "Возвращает значения указанного индикатора (IndCode) для банка в заданном диапазоне дат.\n\n"
                    "Принимаемые параметры (JSON, request body):\n\n"
                    "- `reg_number` (integer) — регистрационный номер банка (целое положительное число). "
                    "Используется для идентификации кредитной организации в базе ЦБ РФ.\n\n"
                    "- `ind_code` (string) — код индикатора (numsc / IndCode). Строковое значение, по которому "
                    "парсер ищет конкретный показатель в форме F101.\n\n"
                    "- `date_from` (datetime) — начало периода (ISO-8601). Дата/время (строка в ISO-формате), "
                    "определяющая нижнюю границу интервала выборки (парсер ожидает naive datetime — tzinfo отбрасывается).\n\n"
                    "- `date_to` (datetime) — конец периода (ISO-8601). Дата/время (строка в ISO-формате), "
                    "определяющая верхнюю границу интервала выборки (парсер ожидает naive datetime — tzinfo отбрасывается).\n\n"
                    "Возвращаемые поля (200 OK, JSON):\n\n"
                    "- `bank_reg_number` (string) — регистрационный номер банка (тот же, что в запросе), используется для "
                    "связи данных с организацией.\n\n"
                    "- `date` (datetime) — дата записи (поле dt из F101) в формате ISO 8601 — дата, к которой привязано "
                    "значение индикатора.\n\n"
                    "- `pln` (string) — раздел формы (например, 'А', 'Б', 'В', 'Г') — указывает на раздел баланса, "
                    "где находится индикатор.\n\n"
                    "- `ap` (integer: 1 или 2) — сторона/тип показателя: 1 — актив, 2 — пассив (ChoiceField в "
                    "сериализаторе).\n\n"
                    "- `vitg` (float) — входящий итог (vitg) — значение на начало периода / входящая сумма.\n\n"
                    "- `iitg` (float) — исходящий итог (iitg) — значение на конец периода / итоговое значение.\n\n"
            ),
            request=BankIndicatorRequestSerializer,
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
                        response=BankIndicatorDataSerializer,
                        description=(
                                "Успешный ответ — объект с данными индикатора:\n\n"
                                "- `bank_reg_number` (string)\n"
                                "- `date` (datetime)\n"
                                "- `pln` (string)\n"
                                "- `ap` (1 или 2)\n"
                                "- `vitg` (float)\n"
                                "- `iitg` (float)\n"
                        )
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
        in_serializer = BankIndicatorRequestSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        reg_number = in_serializer.validated_data['reg_number']
        ind_code = str(in_serializer.validated_data['ind_code']).strip()
        date_from = in_serializer.validated_data['date_from']
        date_to = in_serializer.validated_data['date_to']

        data = Form101Parser.get_indicator_data(reg_number, ind_code, date_from, date_to)
        if 'message' in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        out_serializer = BankIndicatorDataSerializer(instance=data)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class UniqueIndicatorsAPIView(APIView):
    @extend_schema(
            summary="Список уникальных индикаторов формы F101",
            description=(
                    "Возвращает список уникальных индикаторов (catalog) формы F101.\n\n"
                    "Данные загружаются из локального JSON-файла "
                    "`api_payloads/unique_indicators_clean.json`.\n\n"
                    "Структура ответа (200):\n\n"
                    "- `indicators` — массив объектов, каждый объект содержит поля:\n"
                    "  - `ind_code` (string) — код индикатора;\n"
                    "  - `name` (string) — читабельное название индикатора.\n\n"
                    "Если файл невалиден или при чтении произошла ошибка — возвращается статус 500 с описанием."
            ),
            responses={
                200: OpenApiResponse(
                        response=UniqueIndicatorsSerializer,
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

        out_serializer = UniqueIndicatorsSerializer(instance=data)
        return Response(out_serializer.data, status=status.HTTP_200_OK)
