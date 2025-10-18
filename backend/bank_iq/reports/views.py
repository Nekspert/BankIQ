from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.parsers.interest_rates_parser import InterestRatesCreditParser
from .serializers import InterestRatesCreditResponseSerializer, InterestRatesCreditSerializer


class InterestRatesCreditAPIView(APIView):
    @extend_schema(
            summary="Получение данных о процентных ставках по кредитам",
            description=(
                    "Эндпоинт для получения данных о процентных ставках по кредитам от ЦБ РФ. "
                    "Требуется указать ID публикации, набора данных, разреза и диапазон годов. "
                    "Возвращает структурированные данные, включая значения ставок, описание публикации, "
                    "категории кредитов, единицы измерения и диапазон доступных годов"
            ),
            request=InterestRatesCreditSerializer,
            responses={
                200: OpenApiResponse(
                        response=InterestRatesCreditResponseSerializer,
                        description="Успешный ответ с данными о процентных ставках",
                        examples=[
                            OpenApiExample(
                                    name="Пример ответа для publication_id=14 (В целом по Российской Федерации)",
                                    value={
                                        "DTRange": [{"FromY": 2014, "ToY": 2025}],
                                        "RawData": [
                                            {
                                                "colId": 2,
                                                "date": "2014-02-01T00:00:00",
                                                "digits": 2,
                                                "dt": "Январь 2014",
                                                "element_id": 2,
                                                "measure_id": 2,
                                                "obs_val": 7.35,
                                                "periodicity": "month",
                                                "rowId": 265,
                                                "unit_id": 1
                                            },
                                            {
                                                "colId": 9,
                                                "date": "2025-09-01T00:00:00",
                                                "digits": 2,
                                                "dt": "Август 2025",
                                                "element_id": 9,
                                                "measure_id": 2,
                                                "obs_val": 14.15,
                                                "periodicity": "month",
                                                "rowId": 404,
                                                "unit_id": 1
                                            }
                                        ],
                                        "SType": [
                                            {
                                                "PublName": "В целом по Российской Федерации",
                                                "dsName": "Ставки по кредитам нефинансовым организациям",
                                                "sType": 1
                                            }
                                        ],
                                        "headerData": [
                                            {"elname": "До 30 дней, включая 'до востребования'", "id": 2},
                                            {"elname": "От 1 года до 3 лет", "id": 9}
                                        ],
                                        "units": [
                                            {"id": 1, "val": "% годовых"},
                                            {"id": 2, "val": "%"},
                                            {"id": 3, "val": "млрд руб."},
                                            {"id": 4, "val": "млн долларов США"},
                                            {"id": 5, "val": "месяцев"},
                                            {"id": 6, "val": "млн руб."},
                                            {"id": 7, "val": "единиц"},
                                            {"id": 8, "val": "число опрошенных"},
                                            {"id": 9, "val": "пунктов"},
                                            {"id": 10, "val": "руб."}
                                        ]
                                    }
                            ),
                            OpenApiExample(
                                    name="Пример ответа для publication_id=15 (В территориальном разрезе)",
                                    value={
                                        "DTRange": [{"FromY": 2019, "ToY": 2025}],
                                        "RawData": [
                                            {
                                                "colId": 7,
                                                "element_id": 7,
                                                "measure_id": 23,
                                                "unit_id": 1,
                                                "obs_val": 9.18,
                                                "rowId": 325,
                                                "dt": "Январь 2019",
                                                "periodicity": "month",
                                                "date": "2019-02-01T00:00:00",
                                                "digits": 2
                                            },
                                            {
                                                "colId": 11,
                                                "element_id": 11,
                                                "measure_id": 23,
                                                "unit_id": 1,
                                                "obs_val": 13.41,
                                                "rowId": 404,
                                                "dt": "Август 2025",
                                                "periodicity": "month",
                                                "date": "2025-09-01T00:00:00",
                                                "digits": 2
                                            }
                                        ],
                                        "headerData": [
                                            {"id": 7, "elname": "До 1 года, включая 'до востребования'"},
                                            {"id": 11, "elname": "Свыше 1 года"}
                                        ],
                                        "units": [
                                            {"id": 1, "val": "% годовых"},
                                            {"id": 2, "val": "%"},
                                            {"id": 3, "val": "млрд руб."},
                                            {"id": 4, "val": "млн долларов США"},
                                            {"id": 5, "val": "месяцев"},
                                            {"id": 6, "val": "млн руб."},
                                            {"id": 7, "val": "единиц"},
                                            {"id": 8, "val": "число опрошенных"},
                                            {"id": 9, "val": "пунктов"},
                                            {"id": 10, "val": "руб."}
                                        ],
                                        "SType": [
                                            {
                                                "sType": 1,
                                                "dsName": "Ставки по кредитам нефинансовым организациям в рублях",
                                                "PublName": "В территориальном разрезе"
                                            }
                                        ]
                                    }
                            ),
                            OpenApiExample(
                                    name="Пример ответа для publication_id=16 (В разрезе по видам экономической деятельности)",
                                    value={
                                        "DTRange": [{"FromY": 2019, "ToY": 2025}],
                                        "RawData": [
                                            {
                                                "colId": 11,
                                                "element_id": 11,
                                                "measure_id": 21,
                                                "unit_id": 1,
                                                "obs_val": 10.78,
                                                "rowId": 325,
                                                "dt": "Январь 2019",
                                                "periodicity": "month",
                                                "date": "2019-02-01T00:00:00",
                                                "digits": 2
                                            },
                                            {
                                                "colId": 7,
                                                "element_id": 7,
                                                "measure_id": 21,
                                                "unit_id": 1,
                                                "obs_val": 23.02,
                                                "rowId": 404,
                                                "dt": "Август 2025",
                                                "periodicity": "month",
                                                "date": "2025-09-01T00:00:00",
                                                "digits": 2
                                            }
                                        ],
                                        "headerData": [
                                            {"id": 7, "elname": "До 1 года, включая 'до востребования'"},
                                            {"id": 11, "elname": "Свыше 1 года"}
                                        ],
                                        "units": [
                                            {"id": 1, "val": "% годовых"},
                                            {"id": 2, "val": "%"},
                                            {"id": 3, "val": "млрд руб."},
                                            {"id": 4, "val": "млн долларов США"},
                                            {"id": 5, "val": "месяцев"},
                                            {"id": 6, "val": "млн руб."},
                                            {"id": 7, "val": "единиц"},
                                            {"id": 8, "val": "число опрошенных"},
                                            {"id": 9, "val": "пунктов"},
                                            {"id": 10, "val": "руб."}
                                        ],
                                        "SType": [
                                            {
                                                "sType": 1,
                                                "dsName": "Ставки по кредитам нефинансовым организациям",
                                                "PublName": "В разрезе по видам экономической деятельности"
                                            }
                                        ]
                                    }
                            )
                        ]
                ),
                400: OpenApiResponse(
                        description="Ошибка валидации входных данных.",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка валидации publication_id",
                                    value={"message": "publication_id должен быть равен числу в массиве [14, 15, 16]"}
                            ),
                            OpenApiExample(
                                    name="Ошибка валидации dataset_id",
                                    value={
                                        "message": "dataset_id должен быть равен числу в массиве [25, 26, 27, 28, 29] для publication_id=14"}
                            ),
                            OpenApiExample(
                                    name="Ошибка валидации measure_id",
                                    value={
                                        "message": "measure_id должен быть равен числу в массиве [2, 3, 4] для publication_id=14"}
                            ),
                            OpenApiExample(
                                    name="Ошибка диапазона годов",
                                    value={"message": "from_year не может быть больше to_year"}
                            )
                        ]
                ),
                422: OpenApiResponse(
                        description="Недоступный диапазон годов или отсутствие данных",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка диапазона годов",
                                    value={"message": "Информация доступна только с 0 по 2025 год"}
                            ),
                            OpenApiExample(
                                    name="Нет данных",
                                    value={"message": "Нет данных для указанных параметров"}
                            ),
                            OpenApiExample(
                                    name="Ошибка внешнего API",
                                    value={"message": "Ошибка внешнего API: <описание ошибки>"}
                            )
                        ]
                )
            },
            examples=[
                OpenApiExample(
                        name="Пример запроса для publication_id=14",
                        value={
                            "publication_id": 14,
                            "dataset_id": 25,
                            "measure_id": 2,
                            "from_year": 2020,
                            "to_year": 2025
                        }
                ),
                OpenApiExample(
                        name="Пример запроса для publication_id=15",
                        value={
                            "publication_id": 15,
                            "dataset_id": 30,
                            "measure_id": 23,
                            "from_year": 2019,
                            "to_year": 2025
                        }
                ),
                OpenApiExample(
                        name="Пример запроса для publication_id=16",
                        value={
                            "publication_id": 16,
                            "dataset_id": 35,
                            "measure_id": 21,
                            "from_year": 2019,
                            "to_year": 2025
                        }
                )
            ]
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = InterestRatesCreditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        data = InterestRatesCreditParser.parse(
                publication_id=params.get("publication_id"),
                dataset_id=params.get("dataset_id"),
                measure_id=params.get("measure_id"),
                from_year=params.get("from_year"),
                to_year=params.get("to_year"))

        if "message" in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        response_serializer = InterestRatesCreditResponseSerializer(instance=data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
