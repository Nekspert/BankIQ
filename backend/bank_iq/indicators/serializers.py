from rest_framework import serializers


class BankInfoSerializer(serializers.Serializer):
    bic = serializers.CharField(
            required=True,
            help_text="БИК банка (Bank Identification Code). Уникальный идентификатор банка."
    )
    name = serializers.CharField(
            required=True,
            help_text="Полное наименование кредитной организации."
    )
    reg_number = serializers.CharField(
            required=True,
            help_text="Регистрационный номер организации в базе ЦБ РФ."
    )
    internal_code = serializers.CharField(
            required=True,
            help_text="Внутренний код/идентификатор банка в источнике данных."
    )
    registration_date = serializers.DateTimeField(
            required=True,
            help_text="Дата регистрации организации (ISO 8601)."
    )
    region_code = serializers.CharField(
            required=True,
            help_text="Код региона (региональный номер/код)."
    )
    tax_id = serializers.CharField(
            required=True,
            help_text="Идентификатор налогоплательщика (ИНН) или другой налоговый идентификатор, если присутствует."
    )


class AllBanksSerializer(serializers.Serializer):
    banks = BankInfoSerializer(
            many=True,
            help_text="Список банков, каждый элемент — структура BankInfoSerializer."
    )


class RegNumberSerializer(serializers.Serializer):
    reg_number = serializers.IntegerField(
            required=True,
            help_text="Регистрационный номер банка (целое положительное число)."
    )


class DateTimesSerializer(serializers.Serializer):
    datetimes = serializers.ListSerializer(
            child=serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%Z'),
            help_text="Список меток времени (datetime), доступные даты для формы F101."
    )


class RegNumAndDatetimeSerializer(serializers.Serializer):
    reg_number = serializers.IntegerField(
            required=True,
            help_text="Регистрационный номер банка (целое положительное число)."
    )
    dt = serializers.DateTimeField(
            required=True,
            format='%Y-%m-%dT%H:%M:%S%Z',
            help_text="Дата/метка времени в формате ISO 8601."
    )

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        dt = validated['dt']
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        validated['dt'] = dt
        return validated


class IndicatorSerializer(serializers.Serializer):
    name = serializers.CharField(
            required=True,
            help_text="Читабельное название индикатора (показателя) формы 101."
    )
    ind_code = serializers.CharField(
            required=True,
            help_text="Код индикатора (IndCode / numsc) — строковое значение, используется для сопоставления."
    )
    ind_id = serializers.IntegerField(
            required=True,
            help_text="Внутренний идентификатор индикатора (IndID) из каталога индикаторов."
    )
    ind_type = serializers.CharField(
            required=True,
            help_text="Тип индикатора (IndType) — справочная метка/категория индикатора."
    )
    ind_chapter = serializers.CharField(
            required=True,
            help_text="Глава/раздел в каталоге индикаторов (IndChapter)."
    )


class IndicatorsSerializer(serializers.Serializer):
    indicators = IndicatorSerializer(
            many=True,
            help_text="Список доступных индикаторов (catalog) — каждый элемент описан IndicatorSerializer."
    )


class BankIndicatorRequestSerializer(serializers.Serializer):
    reg_number = serializers.IntegerField(
            required=True,
            help_text="Регистрационный номер банка (целое положительное число)."
    )
    ind_code = serializers.CharField(
            required=True,
            help_text="Код индикатора (IndCode / numsc) — строковое значение."
    )
    date_from = serializers.DateTimeField(
            required=True,
            help_text="Начальная дата диапазона (ISO-8601)."
    )
    date_to = serializers.DateTimeField(
            required=True,
            help_text="Конечная дата диапазона (ISO-8601)."
    )

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        for k in ('date_from', 'date_to'):
            dt = validated.get(k)
            if dt.tzinfo is not None:
                validated[k] = dt.replace(tzinfo=None)
        return validated


class BankIndicatorDataSerializer(serializers.Serializer):
    bank_reg_number = serializers.CharField(
            required=True,
            help_text="Регистрационный номер банка (используем для связывания данных с организацией)."
    )
    date = serializers.DateTimeField(
            required=True,
            help_text="Дата записи (поле dt из F101) в формате datetime (ISO 8601)."
    )
    pln = serializers.CharField(
            required=True,
            help_text="Раздел формы (например, 'А', 'Б', 'В', 'Г')."
    )
    ap = serializers.ChoiceField(
            required=True,
            choices=((1, 'Актив'), (2, 'Пассив')),
            help_text="Сторона/тип показателя: 1 — актив, 2 — пассив."
    )
    vitg = serializers.FloatField(
            required=True,
            help_text="Входящий итог (vitg) — значение на начало периода / входящая сумма."
    )
    iitg = serializers.FloatField(
            required=True,
            help_text="Исходящий итог (iitg) — значение на конец периода / итоговое значение."
    )


class UniqueIndicatorSerializer(serializers.Serializer):
    name = serializers.CharField(
            required=True,
            help_text="Читабельное название индикатора (показателя) формы 101."
    )
    ind_code = serializers.CharField(
            required=True,
            help_text="Код индикатора (IndCode / numsc) — строковое значение, используется для сопоставления."
    )


class UniqueIndicatorsSerializer(serializers.Serializer):
    indicators = UniqueIndicatorSerializer(
            many=True,
            help_text="Список доступных индикаторов (catalog) — каждый элемент описан UniqueIndicatorSerializer."
    )
