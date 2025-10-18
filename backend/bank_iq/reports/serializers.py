import datetime

from rest_framework import serializers


class InterestRatesCreditSerializer(serializers.Serializer):
    """
        cls.publication_id = publication_id
        cls.dataset_id = dataset_id
        cls.measure_id = measure_id
        cls.from_year = from_year
        cls.to_year = to_year
    """
    publication_id = serializers.IntegerField(
            required=True,
            help_text="ID публикации. Допустимые значения: 14 (В целом по Российской Федерации), "
                      "15 (В территориальном разрезе), 16 (В разрезе по видам экономической деятельности)."
    )
    dataset_id = serializers.IntegerField(
            required=True,
            help_text="ID набора данных. Допустимые значения: 25 (Ставки по кредитам нефинансовым организациям), "
                      "26 (Ставки по кредитам нефинансовым организациям-субъектам МСП), "
                      "27 (Ставки по кредитам физическим лицам), 28 (Ставки по автокредитам), "
                      "29 (Ставки по ипотечным жилищным кредитам)."
    )
    measure_id = serializers.IntegerField(
            required=True,
            help_text="ID разреза. Допустимые значения: 2 (В рублях), 3 (В долларах США), 4 (В евро)."
    )
    from_year = serializers.IntegerField(
            required=True,
            help_text="Год начала периода. Должен быть не больше to_year."
    )
    to_year = serializers.IntegerField(
            required=True,
            help_text="Год окончания периода. Должен быть не больше текущего года."
    )

    def validate_publication_id(self, value: int):
        if value in (14, 15, 16):
            return value
        raise serializers.ValidationError({"message": "publication_id должен быть равен числу в массиве [14, 15, 16]"})

    def validate_dataset_id(self, value: int):
        if value in (25, 26, 27, 28, 29):
            return value
        raise serializers.ValidationError(
                {"message": "dataset_id должен быть равен числу в массиве [25, 26, 27, 28, 29]"})

    def validate_measure_id(self, value: int):
        if value in (2, 3, 4):
            return value
        raise serializers.ValidationError({"message": "measure_id должен быть равен числу в массиве [2, 3, 4]"})

    def validate(self, data):
        from_year = data.get('from_year')
        to_year = data.get('to_year')
        if from_year and to_year:
            if from_year > to_year:
                raise serializers.ValidationError({"message": "from_year не может быть больше to_year"})
            if to_year > datetime.datetime.now().year:
                raise serializers.ValidationError({"message": "to_year не может быть больше текущего года"})
        return data


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


class InterestRatesCreditResponseSerializer(serializers.Serializer):
    DTRange = DTRangeSerializer(many=True, help_text="Диапазон доступных годов для данных.")
    RawData = DataItemSerializer(many=True, help_text="Список данных о процентных ставках.")
    SType = STypeSerializer(many=True, help_text="Информация о публикации и наборе данных.")
    headerData = HeaderDataSerializer(many=True, help_text="Описание элементов (категорий кредитов).")
    units = UnitSerializer(many=True, help_text="Список единиц измерения.")
