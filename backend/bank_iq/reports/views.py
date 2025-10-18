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
                    "категории кредитов и единицы измерения."
            ),
            request=InterestRatesCreditSerializer,
            responses={
                200: OpenApiResponse(
                        response=InterestRatesCreditResponseSerializer,
                        description="Успешный ответ с данными о процентных ставках.",
                        examples=[
                            OpenApiExample(
                                    name="Пример успешного ответа",
                                    value={
                                        "DTRange": [{"FromY": 2014, "ToY": 2025}],
                                        "RawData": [
                                            {"colId": 4,
                                             "date": "2025-06-01T00:00:00",
                                             "digits": 2,
                                             "dt": "Май 2025",
                                             "element_id": 4,
                                             "measure_id": 2,
                                             "obs_val": 23.95,
                                             "periodicity": "month",
                                             "rowId": 401,
                                             "unit_id": 1}
                                        ],
                                        "SType": [
                                            {"PublName": "В целом по Российской Федерации",
                                             "dsName": "Ставки по кредитам нефинансовым организациям",
                                             "sType": 1}
                                        ],
                                        "headerData": [{"elname": "До 30 дней, включая 'до востребования'", "id": 2}],
                                        "units": [{"id": 1, "val": "% годовых"}]
                                    }
                            )
                        ]
                ),
                400: OpenApiResponse(
                        description="Ошибка валидации входных данных.",
                        examples=[
                            OpenApiExample(
                                    name="Ошибка валидации",
                                    value={"message": "publication_id должен быть равен числу в массиве [14, 15, 16]"}),
                            OpenApiExample(
                                    name="Ошибка диапазона годов",
                                    value={"message": "from_year не может быть больше to_year"})
                        ]
                ),
                422: OpenApiResponse(
                        description="Недоступный диапазон годов.",
                        examples=[
                            OpenApiExample(name="Ошибка диапазона годов",
                                           value={"message": "Информация доступна только с 2014 по 2025 год"})
                        ]
                )
            },
            examples=[
                OpenApiExample(
                        name="Пример успешного ответа",
                        value={
                            "DTRange": [{"FromY": 2014, "ToY": 2025}],
                            "RawData": [{
                                "colId": 2,
                                "date": "2014-02-01T00:00:00",
                                "digits": 2,
                                "dt": "Январь 2014",
                                "element_id": 2,
                                "measure_id": 2,
                                "obs_val": 7.35,
                                "periodicity": "month",
                                "rowId": 265,
                                "unit_id": 1},
                                {"colId": 9,
                                 "date": "2025-09-01T00:00:00",
                                 "digits": 2,
                                 "dt": "Август 2025",
                                 "element_id": 9,
                                 "measure_id": 2,
                                 "obs_val": 14.15,
                                 "periodicity": "month",
                                 "rowId": 404,
                                 "unit_id": 1}
                            ],
                            "SType": [{
                                "PublName": "В целом по Российской Федерации",
                                "dsName": "Ставки по кредитам нефинансовым организациям",
                                "sType": 1}
                            ],
                            "headerData": [{"elname": "До 30 дней, включая 'до востребования'", "id": 2},
                                           {"elname": "От 1 года до 3 лет", "id": 9}],
                            "units": [{"id": 1, "val": "% годовых"},
                                      {"id": 2, "val": "%"}]
                        }
                ),
                OpenApiExample(name="Пример запроса",
                               value={
                                   "publication_id": 14,
                                   "dataset_id": 25,
                                   "measure_id": 2,
                                   "from_year": 2020,
                                   "to_year": 2025}),
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
