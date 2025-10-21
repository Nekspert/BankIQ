import datetime
from abc import ABC, abstractmethod

from rest_framework import serializers

from core.utils.meta import CombinedMeta


class BaseAPISerializer(serializers.Serializer, ABC, metaclass=CombinedMeta):
    from_year = serializers.IntegerField(
            required=True,
            help_text="Год начала периода. Должен быть не больше to_year."
    )
    to_year = serializers.IntegerField(
            required=True,
            help_text="Год окончания периода. Должен быть не больше текущего года."
    )

    def validate(self, data):
        from_year = data.get("from_year")
        to_year = data.get("to_year")
        if from_year and to_year:
            if from_year > to_year:
                raise serializers.ValidationError({"message": "from_year не может быть больше to_year"})
            if to_year > datetime.datetime.now().year:
                raise serializers.ValidationError({"message": "to_year не может быть больше текущего года"})
        return data

    @abstractmethod
    def validate_publication_id(self, value: int):
        pass

    @abstractmethod
    def validate_dataset_id(self, value: int):
        pass

    @abstractmethod
    def validate_measure_id(self, value: int):
        pass


class InterestRatesCreditSerializer(BaseAPISerializer):
    publication_id = serializers.IntegerField(
            required=True,
            help_text="ID публикации. Допустимые значения: 14 (В целом по Российской Федерации), "
                      "15 (В территориальном разрезе), 16 (В разрезе по видам экономической деятельности)."
    )
    dataset_id = serializers.IntegerField(
            required=True,
            help_text="ID набора данных. Зависит от publication_id:\n"
                      "- Для 14: 25 (Ставки по кредитам нефинансовым организациям), "
                      "26 (Ставки по кредитам нефинансовым организациям-субъектам МСП), "
                      "27 (Ставки по кредитам физическим лицам), 28 (Ставки по автокредитам), "
                      "29 (Ставки по ипотечным жилищным кредитам).\n"
                      "- Для 15: 30 (Ставки по кредитам нефинансовым организациям в рублях), "
                      "31 (Ставки по кредитам нефинансовым организациям-субъектам МСП в рублях), "
                      "32 (Ставки по кредитам физическим лицам в рублях), 33 (Ставки по автокредитам в рублях), "
                      "34 (Ставки по ипотечным жилищным кредитам).\n"
                      "- Для 16: 35 (Ставки по кредитам нефинансовым организациям), "
                      "36 (Ставки по кредитам нефинансовым организациям-субъектам МСП)."
    )
    measure_id = serializers.IntegerField(
            required=True,
            help_text="ID разреза. Зависит от publication_id:\n"
                      "- Для 14: 2 (В рублях), 3 (В долларах США), 4 (В евро).\n"
                      "- Для 15: 23 (Центральный федеральный округ), 42 (Северо-Западный федеральный округ), "
                      "55 (Южный федеральный округ), 64 (Северо-Кавказский федеральный округ), "
                      "72 (Приволжский федеральный округ), 87 (Уральский федеральный округ), "
                      "95 (Сибирский федеральный округ), 106 (Дальневосточный федеральный округ).\n"
                      "- Для 16: 7 (Сельское хозяйство), 8 (Добыча полезных ископаемых), 9 (Обрабатывающие "
                      "производства),"
                      "10 (Обеспечение электрической энергией), 11 (Водоснабжение), 12 (Строительство), "
                      "13 (Торговля), 14 (Транспортировка), 15 (Гостиницы), 16 (Информация и связь), "
                      "17 (Недвижимость), 18 (Профессиональная деятельность), 19 (Образование), "
                      "20 (Культура и спорт), 21 (Прочее)."
    )

    def validate_publication_id(self, value: int):
        if value in (14, 15, 16):
            return value
        raise serializers.ValidationError({"message": "publication_id должен быть равен числу в массиве [14, 15, 16]"})

    def validate_dataset_id(self, value: int):
        publication_id = self.initial_data.get('publication_id')
        valid_datasets = {
            14: (25, 26, 27, 28, 29),
            15: (30, 31, 32, 33, 34),
            16: (35, 36)
        }
        if publication_id not in valid_datasets:
            raise serializers.ValidationError({"message": "publication_id должен быть указан для проверки dataset_id"})
        if value not in valid_datasets.get(publication_id):
            values = list(valid_datasets.get(publication_id))
            raise serializers.ValidationError(
                    {"message": f"dataset_id должен быть равен числу в массиве {values}"
                                f" для publication_id={publication_id}"})
        return value

    def validate_measure_id(self, value: int):
        publication_id = self.initial_data.get('publication_id')
        valid_measures = {
            14: (2, 3, 4),
            15: (23, 42, 55, 64, 72, 87, 95, 106),
            16: (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)
        }
        if publication_id not in valid_measures:
            raise serializers.ValidationError({"message": "publication_id должен быть указан для проверки measure_id"})
        if value not in valid_measures.get(publication_id):
            values = list(valid_measures.get(publication_id))
            raise serializers.ValidationError({"message": f"measure_id должен быть равен числу в массиве {values}"
                                                          f" для publication_id={publication_id}"})
        return value


class InterestRatesDepositSerializer(BaseAPISerializer):
    publication_id = serializers.IntegerField(
            required=True,
            help_text="ID публикации. Допустимые значения: 18 (В целом по Российской Федерации), "
                      "19 (В территориальном разрезе).")
    dataset_id = serializers.IntegerField(
            required=True,
            help_text="ID набора данных. Зависит от publication_id:\n"
                      "- Для 18: 37 (Ставки по вкладам (депозитам) физических лиц), "
                      "38 (Ставки по вкладам (депозитам) нефинансовых организаций).\n"
                      "- Для 19: 39 (Ставки по вкладам (депозитам) физических лиц в рублях), "
                      "40 (Ставки по вкладам (депозитам) нефинансовых организаций в рублях).")
    measure_id = serializers.IntegerField(
            required=True,
            help_text="ID разреза. Зависит от publication_id:\n"
                      "- Для 18: 2 (В рублях), 3 (В долларах США), 4 (В евро).\n"
                      "- Для 19: 23 (Центральный федеральный округ), 42 (Северо-Западный федеральный округ), "
                      "55 (Южный федеральный округ), 64 (Северо-Кавказский федеральный округ), "
                      "72 (Приволжский федеральный округ), 87 (Уральский федеральный округ), "
                      "95 (Сибирский федеральный округ), 106 (Дальневосточный федеральный округ)."
    )

    def validate_publication_id(self, value: int):
        if value in (18, 19):
            return value
        raise serializers.ValidationError({"message": "publication_id должен быть равен числу в массиве [18, 19]"})

    def validate_dataset_id(self, value: int):
        publication_id = self.initial_data.get('publication_id')
        valid_datasets = {
            18: (37, 38),
            19: (39, 40),
        }
        if publication_id not in valid_datasets:
            raise serializers.ValidationError({"message": "publication_id должен быть указан для проверки dataset_id"})
        if value not in valid_datasets.get(publication_id):
            values = list(valid_datasets.get(publication_id))
            raise serializers.ValidationError(
                    {"message": f"dataset_id должен быть равен числу в массиве {values}"
                                f" для publication_id={publication_id}"})
        return value

    def validate_measure_id(self, value: int):
        publication_id = self.initial_data.get('publication_id')
        valid_measures = {
            18: (2, 3, 4),
            19: (23, 42, 55, 64, 72, 87, 95, 106),
        }
        if publication_id not in valid_measures:
            raise serializers.ValidationError({"message": "publication_id должен быть указан для проверки measure_id"})
        if value not in valid_measures.get(publication_id):
            values = list(valid_measures.get(publication_id))
            raise serializers.ValidationError({"message": f"measure_id должен быть равен числу в массиве {values}"
                                                          f" для publication_id={publication_id}"})
        return value


class DTRangeSerializer(serializers.Serializer):
    FromY = serializers.IntegerField(help_text="Год начала доступного диапазона данных.")
    ToY = serializers.IntegerField(help_text="Год окончания доступного диапазона данных.")


class DataItemSerializer(serializers.Serializer):
    colId = serializers.IntegerField(help_text="ID столбца.")
    date = serializers.DateTimeField(help_text="Дата в формате YYYY-MM-DDThh:mm:ss.")
    digits = serializers.IntegerField(help_text="Количество знаков после запятой.")
    dt = serializers.CharField(help_text="Человекочитаемое представление даты, например, 'Май 2025'.")
    element_id = serializers.IntegerField(help_text="ID элемента (например, категории кредитов).")
    measure_id = serializers.IntegerField(help_text="ID разреза (например, 2 для рублёвых ставок).")
    obs_val = serializers.FloatField(help_text="Значение показателя (например, процентная ставка).")
    periodicity = serializers.CharField(help_text="Периодичность данных (например, 'month').")
    rowId = serializers.IntegerField(help_text="ID строки.")
    unit_id = serializers.IntegerField(help_text="ID единицы измерения.")


class STypeSerializer(serializers.Serializer):
    PublName = serializers.CharField(help_text="Название публикации.")
    dsName = serializers.CharField(help_text="Название набора данных.")
    sType = serializers.IntegerField(help_text="Тип набора данных.")


class HeaderDataSerializer(serializers.Serializer):
    elname = serializers.CharField(help_text="Название элемента (например, 'До 30 дней').")
    id = serializers.IntegerField(help_text="ID элемента.")


class UnitSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID единицы измерения.")
    val = serializers.CharField(help_text="Название единицы измерения (например, '% годовых').")


class InterestRatesResponseSerializer(serializers.Serializer):
    DTRange = DTRangeSerializer(many=True, help_text="Диапазон доступных годов для данных.")
    RawData = DataItemSerializer(many=True, help_text="Список данных о процентных ставках.")
    SType = STypeSerializer(many=True, help_text="Информация о публикации и наборе данных.")
    headerData = HeaderDataSerializer(many=True, help_text="Описание элементов (категорий кредитов).")
    units = UnitSerializer(many=True, help_text="Список единиц измерения.")
