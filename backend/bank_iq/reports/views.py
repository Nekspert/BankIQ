from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.parsers.rest.cbr_parser import CbrAPIParser
from .serializers import (CheckRequestSerializer,
                          CheckResponseSerializer,
                          CheckYearsResponseSerializer,
                          InterestRatesCreditSerializer,
                          InterestRatesDepositSerializer,
                          ResponseSerializer)


class CheckValidDataAPIView(APIView):
    @extend_schema(
            summary="Список публикаций / датасетов / разрезов / лет (проверка доступных параметров)",
            description=(
                    "Эндпоинт для получения возможных значений для параметров запроса к API ЦБ: "
                    "список публикаций, датасетов для указанной публикации, разрезов (measures) для указанного датасета"
                    " и диапазон доступных лет для указанного датасета + разреза. "
                    "Если не передавать параметры — вернётся список публикаций. "
                    "Если передать только `publication_id` — вернутся датасеты для этой публикации. "
                    "Если передать `publication_id` и `dataset_id` — вернутся `measures` для датасета. "
                    "Если передать все три — вернётся диапазон лет (`FromYear`, `ToYear`)."
            ),
            request=CheckRequestSerializer,
            responses={
                200: OpenApiResponse(
                        response=CheckResponseSerializer(many=True),
                        description="Успешный ответ — объект с одним из ключей: `publication_ids` / `dataset_ids` / "
                                    "`measure_ids` / `years`.",
                        examples=[
                            OpenApiExample(
                                    name="Пример ответа — список публикаций",
                                    value={
                                        "publication_ids": [
                                            {"id": 14, "title": "В целом по Российской Федерации",
                                             "status": "value [searchable]"},
                                            {"id": 15, "title": "В территориальном разрезе",
                                             "status": "value [searchable]"},
                                            {"id": 16, "title": "По видам экономической деятельности",
                                             "status": "value [searchable]"},
                                        ]
                                    },
                            ),
                            OpenApiExample(
                                    name="Пример ответа — список датасетов для publication_id=14",
                                    value={
                                        "dataset_ids": [
                                            {"id": 25, "title": "Ставки по кредитам нефинансовым организациям",
                                             "status": "value [searchable]"},
                                            {"id": 26, "title": "Ставки по кредитам МСП",
                                             "status": "value [searchable]"},
                                            {"id": 27, "title": "Ставки по кредитам физическим лицам",
                                             "status": "value [searchable]"},
                                        ]
                                    },
                            ),
                            OpenApiExample(
                                    name="Пример ответа — список measures для dataset_id=25",
                                    value={
                                        "measure_ids": [
                                            {"id": 2, "title": "В рублях", "status": "value [searchable]"},
                                            {"id": 3, "title": "В долларах США", "status": "value [searchable]"},
                                            {"id": 4, "title": "В евро", "status": "value [searchable]"},
                                        ]
                                    },
                            ),
                            OpenApiExample(
                                    name="Пример ответа — years для dataset+measure",
                                    value={"years": [2014, 2025]},
                            ),
                        ],
                ),
                400: OpenApiResponse(
                        description="Ошибка валидации входных данных.",
                        examples=[
                            OpenApiExample(name="Неправильный publication_id", value={
                                "message": "publication_id должен быть числом из допустимого набора"}),
                            OpenApiExample(name="Неправильный dataset_id", value={
                                "message": "dataset_id должен соответствовать указанной publication_id"}),
                            OpenApiExample(name="Неправильный measure_id", value={
                                "message": "measure_id должен соответствовать указанному dataset_id / publication_id"}),
                        ],
                ),
                422: OpenApiResponse(
                        description="Пустой результат или ошибка внешнего API.",
                        examples=[
                            OpenApiExample(name="Нет данных или пустой ответ",
                                           value={"message": "Нет данных для указанных параметров"}),
                            OpenApiExample(name="Ошибка внешнего API",
                                           value={"message": "Ошибка внешнего API: <описание ошибки>"}),
                        ],
                ),
            },
            examples=[
                OpenApiExample(name="Пример запроса — получить все публикации (пустой body)", value={}),
                OpenApiExample(name="Пример запроса — получить датасеты для publication_id=14",
                               value={"publication_id": 14}),
                OpenApiExample(name="Пример запроса — получить measures для dataset_id=25 (publication_id=14)",
                               value={"publication_id": 14, "dataset_id": 25}),
                OpenApiExample(name="Пример запроса — получить years для publication+dataset+measure",
                               value={"publication_id": 14, "dataset_id": 25, "measure_id": 2}),
            ],
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = CheckRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        data = CbrAPIParser.check_available_params(
                publication_id=params.get("publication_id"),
                dataset_id=params.get("dataset_id"),
                measure_id=params.get("measure_id"),
        )

        if "message" in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if "publication_ids" in data:
            resp_ser = CheckResponseSerializer(instance=data["publication_ids"], many=True)
            return Response(resp_ser.data, status=status.HTTP_200_OK)

        if "dataset_ids" in data:
            resp_ser = CheckResponseSerializer(instance=data["dataset_ids"], many=True)
            return Response(resp_ser.data, status=status.HTTP_200_OK)

        if "measure_ids" in data:
            resp_ser = CheckResponseSerializer(instance=data["measure_ids"], many=True)
            return Response(resp_ser.data, status=status.HTTP_200_OK)

        if "years" in data:
            resp_ser = CheckYearsResponseSerializer(instance={"years": data["years"]})
            return Response(resp_ser.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)


class InterestRatesCreditAPIView(APIView):
    @extend_schema(
            summary="Получение данных о процентных ставках по кредитам",
            description=(
                    "Эндпоинт для получения данных о процентных ставках по кредитам от ЦБ РФ. "
                    "Требуется указать ID публикации, набора данных, разреза и диапазон годов. "
                    "Возвращаемая структура — объект с полями: "
                    "`DTRange`, `RawData`, `SType`, `headerData`, `units`. "
                    "Поле `RawData` содержит массив наблюдений (элементы с `obs_val`, `date`, `element_id` и т.д.)."
            ),
            request=InterestRatesCreditSerializer,
            responses={
                200: OpenApiResponse(
                        response=ResponseSerializer,
                        description="Успешный ответ — объект с полями `DTRange`, `RawData`, `SType`, `headerData`, `units`.",
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
                                                "unit_id": 1,
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
                                                "unit_id": 1,
                                            },
                                        ],
                                        "SType": [
                                            {
                                                "PublName": "В целом по Российской Федерации",
                                                "dsName": "Ставки по кредитам нефинансовым организациям",
                                                "sType": 1,
                                            }
                                        ],
                                        "headerData": [{"elname": "До 30 дней, включая 'до востребования'", "id": 2}],
                                        "units": [{"id": 1, "val": "% годовых"}],
                                    },
                            )
                        ],
                ),
                400: OpenApiResponse(
                        description="Ошибка валидации входных данных.",
                        examples=[
                            OpenApiExample(name="Ошибка валидации publication_id", value={
                                "message": "publication_id должен быть равен числу в массиве [14, 15, 16]"}),
                            OpenApiExample(name="Ошибка диапазона годов",
                                           value={"message": "from_year не может быть больше to_year"}),
                        ],
                ),
                422: OpenApiResponse(
                        description="Недоступный диапазон годов или отсутствие данных / ошибка внешнего API.",
                        examples=[
                            OpenApiExample(name="Ошибка диапазона годов",
                                           value={"message": "Информация доступна только с 0 по 2025 год"}),
                            OpenApiExample(name="Нет данных", value={"message": "Нет данных для указанных параметров"}),
                            OpenApiExample(name="Ошибка внешнего API",
                                           value={"message": "Ошибка внешнего API: <описание ошибки>"}),
                        ],
                ),
            },
            examples=[
                OpenApiExample(name="Пример запроса для publication_id=14",
                               value={"publication_id": 14, "dataset_id": 25, "measure_id": 2, "from_year": 2020,
                                      "to_year": 2025}),
            ],
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = InterestRatesCreditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        data = CbrAPIParser.parse(
                publication_id=params.get("publication_id"),
                dataset_id=params.get("dataset_id"),
                measure_id=params.get("measure_id"),
                from_year=params.get("from_year"),
                to_year=params.get("to_year"),
        )

        if "message" in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        response_serializer = ResponseSerializer(instance=data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class InterestRatesDepositAPIView(APIView):
    @extend_schema(
            summary="Получение данных о процентных ставках по депозитам",
            description=(
                    "Эндпоинт для получения данных о процентных ставках по депозитам от ЦБ РФ. "
                    "Требуется указать ID публикации, набора данных, разреза и диапазон годов. "
                    "Возвращаемая структура — объект с полями: "
                    "`DTRange`, `RawData`, `headerData`, `units`, `SType`. "
                    "Поле `RawData` содержит массив наблюдений (элементы с `obs_val`, `date`, `element_id` и т.д.)."
            ),
            request=InterestRatesDepositSerializer,
            responses={
                200: OpenApiResponse(
                        description="Успешный ответ — объект с полями `DTRange`, `RawData`, `headerData`, `units`, "
                                    "`SType`.",
                        examples=[
                            OpenApiExample(
                                    name="Пример ответа для publication_id=18, dataset_id=37, measure_id=2",
                                    value={
                                        "RawData": [
                                            {"colId": 1, "element_id": 1, "measure_id": 2, "unit_id": 1,
                                             "obs_val": 1.98, "rowId": 265, "dt": "Январь 2014", "periodicity": "month",
                                             "date": "2014-02-01T00:00:00", "digits": 2},
                                            {"colId": 1, "element_id": 1, "measure_id": 2, "unit_id": 1,
                                             "obs_val": 10.81, "rowId": 404, "dt": "Август 2025",
                                             "periodicity": "month", "date": "2025-09-01T00:00:00", "digits": 2}
                                        ],
                                        "headerData": [{"id": 1, "elname": "\"До востребования\""}],
                                        "units": [{"id": 1, "val": "% годовых"}],
                                        "DTRange": [{"FromY": 2014, "ToY": 2025}],
                                        "SType": [{"sType": 1, "dsName": "Ставки по вкладам (депозитам) физических лиц",
                                                   "PublName": "В целом по Российской Федерации"}],
                                    },
                            )
                        ],
                ),
                400: OpenApiResponse(
                        description="Ошибка валидации входных данных.",
                        examples=[
                            OpenApiExample(name="Ошибка валидации publication_id", value={
                                "message": "publication_id должен быть равен числу в массиве [18, 19]"}),
                            OpenApiExample(name="Ошибка диапазона годов",
                                           value={"message": "from_year не может быть больше to_year"}),
                        ],
                ),
                422: OpenApiResponse(
                        description="Недоступный диапазон годов или отсутствие данных / ошибка внешнего API.",
                        examples=[
                            OpenApiExample(name="Ошибка диапазона годов",
                                           value={"message": "Информация доступна только с 0 по 2025 год"}),
                            OpenApiExample(name="Нет данных", value={"message": "Нет данных для указанных параметров"}),
                            OpenApiExample(name="Ошибка внешнего API",
                                           value={"message": "Ошибка внешнего API: <описание ошибки>"}),
                        ],
                ),
            },
            examples=[
                OpenApiExample(name="Пример запроса для publication_id=18",
                               value={"publication_id": 18, "dataset_id": 37, "measure_id": 2, "from_year": 2015,
                                      "to_year": 2025}),
            ],
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = InterestRatesDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        data = CbrAPIParser.parse(
                publication_id=params.get("publication_id"),
                dataset_id=params.get("dataset_id"),
                measure_id=params.get("measure_id"),
                from_year=params.get("from_year"),
                to_year=params.get("to_year"))

        if "message" in data:
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        response_serializer = ResponseSerializer(instance=data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
