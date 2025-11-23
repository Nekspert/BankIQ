from rest_framework import serializers


class BankInfoSerializer(serializers.Serializer):
    bic = serializers.CharField(
            required=True,
            help_text="БИК банка (Bank Identification Code). Уникальный идентификатор банка. Пример: '044525225'."
    )
    name = serializers.CharField(
            required=True,
            help_text="Полное наименование кредитной организации."
    )
    reg_number = serializers.IntegerField(
            required=True,
            help_text="Регистрационный номер организации в базе ЦБ РФ (строка). Пример: '1481'."
    )
    internal_code = serializers.CharField(
            required=True,
            help_text="Внутренний код/идентификатор банка в источнике данных (если доступен)."
    )
    registration_date = serializers.DateTimeField(
            required=True,
            help_text="Дата регистрации организации (ISO 8601). Может содержать смещение часового пояса."
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
            help_text="Регистрационный номер банка (целое положительное число). Пример: 1481."
    )


class DateTimesSerializer(serializers.Serializer):
    datetimes = serializers.ListSerializer(
            child=serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%Z'),
            help_text=(
                "Список доступных дат формы F101. Каждая дата возвращается в ISO-8601. "
                "Если исходный объект содержит tzinfo, DRF может конвертировать в UTC (с суффиксом 'Z')."
            )
    )
