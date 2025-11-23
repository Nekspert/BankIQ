from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.helpers.indicators_db_functions import _create_banks_from_api, \
    _create_or_get_datetimes_request_atomic, _find_existing_dates_request, _get_all_banks_from_db
from core.parsers.soap.form101_parser import Form101Parser
from core.parsers.soap.form123_parser import Form123Parser
from indicators.models import FormType
from .models import Bank, BankDatesResponse
from .serializers import AllBanksSerializer, DateTimesSerializer, RegNumberSerializer


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
